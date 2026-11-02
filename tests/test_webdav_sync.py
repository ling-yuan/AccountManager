import copy
import json
import os
import tempfile
import threading
import unittest
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

os.environ["QT_QPA_PLATFORM"] = "offscreen"

from PyQt5.QtCore import QCoreApplication, QEvent, QEventLoop, QTimer, pyqtSignal
from PyQt5.QtWidgets import QApplication, QDialog
from webdav3.exceptions import RemoteResourceNotFound, ResponseErrorCode

from AccountManager.tools import data_tools
from AccountManager.window import main_window


def make_payload(password="local", group_key="group"):
    return {
        "format": "account_manager_groups_v1",
        "groups": [
            {
                "key": group_key,
                "title": "Accounts",
                "records": [
                    {
                        "id": "shared-id",
                        "name": "Mail",
                        "account": "user",
                        "password": password,
                        "note": "",
                    }
                ],
            }
        ],
    }


class SettingsStub(QDialog):
    signal_tray = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.running_threads = 0

    def on_click_webdav_backup(self):
        pass

    def on_click_webdav_restore(self):
        pass


class WebDAVDataTests(unittest.TestCase):
    def test_merge_preserves_conflicts_and_is_idempotent(self):
        local = make_payload()
        remote = make_payload("remote", "remote-group")
        duplicate = dict(local["groups"][0]["records"][0], id="duplicate-id")
        remote["groups"][0]["records"].append(duplicate)
        other_group = copy.deepcopy(remote["groups"][0])
        other_group.update(key="other-group", title="Other")
        remote["groups"].append(other_group)
        original_local = copy.deepcopy(local)
        original_remote = copy.deepcopy(remote)

        merged = data_tools.DataTool.merge_tab_groups(local, remote)

        self.assertEqual(len(merged["groups"]), 2)
        self.assertEqual(len(merged["groups"][0]["records"]), 2)
        self.assertEqual(
            {record["password"] for record in merged["groups"][0]["records"]},
            {"local", "remote"},
        )
        identifiers = [
            record["id"] for group in merged["groups"] for record in group["records"]
        ]
        self.assertEqual(len(identifiers), len(set(identifiers)))
        self.assertEqual(data_tools.DataTool.merge_tab_groups(merged, remote), merged)
        self.assertEqual(data_tools.DataTool.merge_tab_groups(local, remote), merged)
        self.assertEqual(local, original_local)
        self.assertEqual(remote, original_remote)

    def test_invalid_records_are_rejected(self):
        remote = make_payload()
        remote["groups"][0]["records"] = [None]
        with self.assertRaises(ValueError):
            data_tools.DataTool.merge_tab_groups(make_payload(), remote)

    def test_upload_encryption_and_manual_backup_remain_compatible(self):
        config = SimpleNamespace(
            webdav_protocol="https",
            webdav_host="example.invalid",
            webdav_port="443",
            webdav_path="dav",
            webdav_account="user",
            webdav_password="test-only",
            version="2.3.0",
        )
        client = MagicMock()
        client.check.return_value = True
        uploaded = []

        def capture_upload(remote_path, local_path):
            with open(local_path, encoding="utf-8") as source:
                uploaded.append((remote_path, json.load(source)))

        client.upload_sync.side_effect = capture_upload
        with patch.object(data_tools.WebDAVTools, "config", config), patch.object(
            data_tools, "create_webdav_client_with_proxy", return_value=client
        ):
            webdav = data_tools.WebDAVTools()
            payload = make_payload()
            self.assertTrue(webdav.upload_tab_groups(payload))
            self.assertEqual(len(uploaded), 2)
            self.assertEqual(
                uploaded[-1][0], "AccountManager_Backup/latest_backup.json"
            )
            decrypted = data_tools.EncryptionTools.decrypt_data(
                uploaded[-1][1], config.webdav_password
            )
            self.assertEqual(json.loads(decrypted)["tab_groups"], payload)
            local = MagicMock()
            local.load_tab_groups.return_value = payload
            self.assertTrue(webdav.backup_data(local))
            self.assertEqual(len(uploaded), 4)

            client.check.return_value = False
            client.execute_request.side_effect = RemoteResourceNotFound(
                "AccountManager_Backup/latest_backup.json"
            )
            self.assertIsNone(webdav.download_tab_groups())
            self.assertEqual(
                webdav.download_tab_groups(allow_missing=True),
                {"format": "account_manager_groups_v1", "groups": []},
            )
            client.execute_request.side_effect = ResponseErrorCode(
                "https://example.invalid", 401, "Unauthorized"
            )
            self.assertIsNone(webdav.download_tab_groups(allow_missing=True))
            with patch.object(
                data_tools,
                "create_webdav_client_with_proxy",
                side_effect=OSError("test-only network failure"),
            ):
                self.assertIsNone(webdav.download_tab_groups(allow_missing=True))


class WebDAVWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setQuitOnLastWindowClosed(False)

    def setUp(self):
        self.stack = ExitStack()
        directory = self.stack.enter_context(tempfile.TemporaryDirectory())
        self.config = SimpleNamespace(
            use_systemtray=False,
            data_save_type="sqlite",
            sqlite_path=directory,
            webdav_protocol="https",
            webdav_host="example.invalid",
            webdav_port="443",
            webdav_path="dav",
            webdav_account="user",
            webdav_password="test-only",
        )
        self.remote = make_payload("remote", "remote-group")
        self.events = []
        self.uploads = []
        self.fail_download = False
        self.fail_upload = False
        self.block_upload = False
        self.upload_started = threading.Event()
        self.upload_release = threading.Event()
        for context in (
            patch.object(data_tools, "Config", return_value=self.config),
            patch.object(main_window, "Config", return_value=self.config),
            patch.object(main_window, "SettingsWindow", SettingsStub),
            patch.object(data_tools.WebDAVTools, "config", self.config),
            patch.object(
                data_tools.WebDAVTools,
                "download_tab_groups",
                side_effect=self.download,
            ),
            patch.object(
                data_tools.WebDAVTools,
                "upload_tab_groups",
                side_effect=self.upload,
            ),
        ):
            self.stack.enter_context(context)
        self.database = data_tools.DataTool()
        self.database.save_tab_groups(make_payload())
        self.window = main_window.MainWindow(self.app)

    def tearDown(self):
        self.upload_release.set()
        self.window.stop_webdav_sync()
        self.window.deleteLater()
        QCoreApplication.sendPostedEvents(None, QEvent.DeferredDelete)
        self.app.processEvents()
        self.stack.close()

    def download(self, allow_missing=False):
        self.assertTrue(allow_missing)
        self.events.append("download")
        return None if self.fail_download else copy.deepcopy(self.remote)

    def upload(self, payload):
        self.events.append("upload")
        self.uploads.append(copy.deepcopy(payload))
        if self.block_upload:
            self.block_upload = False
            self.upload_started.set()
            if not self.upload_release.wait(5):
                return False
        if self.fail_upload:
            return False
        self.remote = copy.deepcopy(payload)
        return True

    def wait_until(self, condition):
        if condition():
            return
        loop = QEventLoop()
        timeout = QTimer()
        timeout.setSingleShot(True)
        expired = []
        timeout.timeout.connect(lambda: (expired.append(True), loop.quit()))
        probe = QTimer()
        probe.timeout.connect(lambda: loop.quit() if condition() else None)
        probe.start(5)
        timeout.start(5000)
        loop.exec_()
        probe.stop()
        timeout.stop()
        self.assertFalse(expired, "WebDAV task did not finish")

    def drain_tasks(self):
        self.app.processEvents()
        self.wait_until(
            lambda: self.window.webdav_sync_thread is None
            and not self.window.webdav_task_timer.isActive()
            and not self.window._webdav_pull_pending
            and not self.window._webdav_upload_pending
        )

    def edit_password(self, password):
        self.window.set_data(next(iter(self.window.current_store())))
        self.window.lineEdit_password.setText(password)
        self.window.on_click_modify()

    def test_startup_merges_and_uploads(self):
        self.drain_tasks()
        self.assertEqual(self.events, ["download", "upload"])
        payload = self.window.build_tab_groups_payload()
        self.assertEqual(len(payload["groups"][0]["records"]), 2)
        self.assertEqual(self.remote, payload)
        self.assertEqual(self.database.load_tab_groups(), payload)

    def test_saved_record_change_uploads_automatically(self):
        self.drain_tasks()
        self.events.clear()
        self.edit_password("edited")
        self.drain_tasks()
        self.assertEqual(self.events, ["upload"])
        self.assertEqual(self.remote, self.window.build_tab_groups_payload())
        self.assertTrue(
            any(
                record["password"] == "edited"
                for record in self.remote["groups"][0]["records"]
            )
        )

    def test_two_hour_sync_merges_and_preserves_unsaved_input(self):
        self.drain_tasks()
        self.events.clear()
        self.remote["groups"][0]["records"].append(
            dict(make_payload()["groups"][0]["records"][0], id="extra", name="Extra")
        )
        self.window.lineEdit_name.setText("Unsaved input")
        self.window.lineEdit_name.setModified(True)
        self.window.textEdit_note.setPlainText("Unsaved note")
        self.window.textEdit_note.document().setModified(True)
        self.assertEqual(self.window.webdav_sync_timer.interval(), 7200000)
        self.assertTrue(self.window.webdav_sync_timer.isActive())
        self.window.webdav_sync_timer.timeout.emit()
        self.drain_tasks()
        self.assertEqual(self.events, ["download", "upload"])
        self.assertEqual(self.window.lineEdit_name.text(), "Unsaved input")
        self.assertTrue(self.window.lineEdit_name.isModified())
        self.assertEqual(self.window.textEdit_note.toPlainText(), "Unsaved note")
        self.assertTrue(self.window.textEdit_note.document().isModified())
        self.assertEqual(self.remote, self.database.load_tab_groups())
        self.assertEqual(len(self.remote["groups"][0]["records"]), 3)

    def test_pending_pull_precedes_local_upload(self):
        self.window.sync_webdav_data()
        self.window.tabWidget.setTabText(0, "Locally renamed")
        self.window.save_tab_groups()
        self.drain_tasks()
        self.assertEqual(self.events, ["download", "upload"])
        self.assertEqual(len(self.remote["groups"]), 2)
        self.assertEqual(
            {
                record["password"]
                for group in self.remote["groups"]
                for record in group["records"]
            },
            {"local", "remote"},
        )
        self.assertEqual(self.remote["groups"][0]["title"], "Locally renamed")

    def test_edit_during_upload_is_uploaded_afterward(self):
        self.drain_tasks()
        self.events.clear()
        self.uploads.clear()
        self.block_upload = True
        self.edit_password("first-edit")
        self.wait_until(self.upload_started.is_set)
        self.edit_password("second-edit")
        self.upload_release.set()
        self.drain_tasks()
        self.assertEqual(self.events, ["upload", "upload"])
        self.assertEqual(self.remote, self.window.build_tab_groups_payload())
        self.assertTrue(
            any(
                record["password"] == "second-edit"
                for record in self.remote["groups"][0]["records"]
            )
        )

    def test_failed_pull_does_not_overwrite_remote_and_retries(self):
        self.fail_download = True
        original_local = self.database.load_tab_groups()
        original_remote = copy.deepcopy(self.remote)
        self.wait_until(
            lambda: self.events == ["download"]
            and self.window.webdav_sync_thread is None
            and self.window.webdav_task_timer.isActive()
        )
        self.assertEqual(self.database.load_tab_groups(), original_local)
        self.assertEqual(self.remote, original_remote)
        self.assertTrue(self.window._webdav_pull_pending)
        self.assertGreater(self.window.webdav_task_timer.remainingTime(), 25000)
        self.fail_download = False
        self.window.webdav_task_timer.start(0)
        self.drain_tasks()
        self.assertEqual(self.events, ["download", "download", "upload"])

    def test_failed_upload_retries_latest_local_snapshot(self):
        self.drain_tasks()
        self.events.clear()
        self.fail_upload = True
        self.edit_password("edited")
        self.wait_until(
            lambda: self.events == ["upload"]
            and self.window.webdav_sync_thread is None
            and self.window.webdav_task_timer.isActive()
        )
        self.assertTrue(self.window._webdav_upload_pending)
        self.fail_upload = False
        self.window.webdav_task_timer.start(0)
        self.drain_tasks()
        self.assertEqual(self.events, ["upload", "upload"])
        self.assertEqual(self.remote, self.window.build_tab_groups_payload())

    def test_unconfigured_webdav_does_not_start_network_tasks(self):
        self.config.webdav_host = ""
        self.drain_tasks()
        self.edit_password("local-only")
        self.drain_tasks()
        self.assertEqual(self.events, [])
        self.assertEqual(
            self.database.load_tab_groups(), self.window.build_tab_groups_payload()
        )

    def test_missing_remote_backup_is_initialized(self):
        self.remote = {"format": "account_manager_groups_v1", "groups": []}
        self.drain_tasks()
        self.assertEqual(self.events, ["download", "upload"])
        self.assertEqual(self.remote, make_payload())

    def test_shutdown_merges_pending_remote_before_upload(self):
        self.window.sync_webdav_data()
        self.window.tabWidget.setTabText(0, "Locally renamed")
        self.window.save_tab_groups()
        self.window.stop_webdav_sync()
        self.assertEqual(self.events, ["download", "upload"])
        self.assertEqual(len(self.remote["groups"]), 2)
        self.assertEqual(
            {
                record["password"]
                for group in self.remote["groups"]
                for record in group["records"]
            },
            {"local", "remote"},
        )
        self.assertEqual(self.remote, self.database.load_tab_groups())


if __name__ == "__main__":
    unittest.main()
