import os
import subprocess
from threading import Thread

import rospkg
from python_qt_binding.QtCore import QTimer, Qt, QModelIndex
from python_qt_binding.QtGui import QPixmap, QImage, QStandardItemModel, QStandardItem, QDoubleValidator
from python_qt_binding.QtWidgets import QWidget, QMessageBox

import rospy
from python_qt_binding import loadUi
from qt_gui.plugin import Plugin
from std_msgs.msg import String
from r3_user_main import R3MonitoringUser
import random


class R3MonitoringPlugin(Plugin):
    def __init__(self, context):
        super(R3MonitoringPlugin, self).__init__(context)
        self.setObjectName('R3MonitoringPlugin')

        self._widget = QWidget()
        ui_file = os.path.join(rospkg.RosPack().get_path('rqt_vive'), 'resource', 'rqt_r3_monitoring.ui')
        loadUi(ui_file, self._widget)

        # Give QObjects reasonable names
        self._widget.setObjectName('R3MonitoringPlugin')
        self._widget.setWindowTitle('R3 Monitoring')
        if context.serial_number() > 1:
            self._widget.setWindowTitle(self._widget.windowTitle() + (' (%d)' % context.serial_number()))

        context.add_widget(self._widget)

        self._widget.btn_start_r3_user.clicked.connect(self.start_r3_user)
        self._widget.btn_stop_r3_user.clicked.connect(self.stop_r3_user)
        self._widget.btn_stop_r3_user.setEnabled(False)
        self.r3_monitoring = R3MonitoringUser('#')
        self.r3_thread = None

        self.hostnames_model = QStandardItemModel(self._widget.listview_robots)
        self.hostnames_model.itemChanged.connect(self.hostnames_model_item_changed)
        self._widget.listview_robots.clicked[QModelIndex].connect(self.hostnames_model_item_selection_changed)
        self.topics_model = QStandardItemModel(self._widget.listview_topics)
        self.topics_model.itemChanged.connect(self.topics_model_item_changed)
        self.timer_watch_r3_topics = QTimer(self)
        self.timer_watch_r3_topics.timeout.connect(self.watch_r3_topics)
        self.timer_watch_r3_topics.start(3000)  # 1 second

    def shutdown_plugin(self):
        # TODO: unregister all publishers here
        pass

    def save_settings(self, plugin_settings, instance_settings):
        # TODO save intrinsic configuration, usually using:
        instance_settings.set_value("SERVER_IP", self._widget.lineedit_r3_host.text())
        instance_settings.set_value("MQTT_PORT", self._widget.lineedit_r3_port.text())

    def restore_settings(self, plugin_settings, instance_settings):
        # TODO restore intrinsic configuration, usually using:
        self._widget.lineedit_r3_host.setText(instance_settings.value("SERVER_IP"))
        self._widget.lineedit_r3_port.setText(instance_settings.value("MQTT_PORT"))

    def system_stats_callback(self, msg):
        if msg.name == "SystemStat":
            for kv in msg.values:
                # print(kv.key, kv.value)
                pass  # todo: update the ui

    def watch_r3_topics(self):
        if self.r3_thread is None:
            return
        for host in self.r3_monitoring.robot_hostnames:
            if self.hostnames_model.findItems(host):
                continue
            print(f"found new robot: {host}")
            item = QStandardItem(host)
            item.setEditable(False)
            item.setSelectable(False)
            item.setCheckable(True)
            item.setCheckState(Qt.Checked)
            item.setToolTip("click to subscribe/unsubscribe")
            self.hostnames_model.appendRow(item)
        self._widget.listview_robots.setModel(self.hostnames_model)

        all_topics = sorted(self.r3_monitoring.publishers.keys())
        for topic in all_topics:
            if self.topics_model.findItems(topic):
                continue
            # print(f"found new topic [{topic}]: \t{str(type(self.r3_monitoring.publishers[topic]['message_object'])).split('.')[-1][:-2]}")
            item = QStandardItem(topic)
            item.setEditable(False)
            item.setSelectable(True)
            item.setCheckable(True)
            item.setCheckState(Qt.Checked)
            self.topics_model.appendRow(item)

            # if topic.endswith("/system_stats"):
            #     self.my_subscribers.append(rospy.Subscriber(topic, DiagnosticStatus, self.system_stats_callback))

        self._widget.listview_topics.setModel(self.topics_model)
        # self._widget.label_robot_hostname.setText(self.r3_monitoring.robot_hostnames[0])

    def start_r3_user(self):
        print('Start_r3_user')
        self.r3_monitoring.client_id = '#'
        host = self._widget.lineedit_r3_host.text()
        port = self._widget.lineedit_r3_port.text()
        print(f"connecting R3 to {host}:{port}")
        if host == "" or port == "":
            return

        self.r3_monitoring.connect(host, int(port))
        # self.r3_monitoring.loop()
        self.r3_thread = Thread(target=self.r3_monitoring.loop)
        self.r3_thread.start()
        self._widget.btn_stop_r3_user.setEnabled(True)
        self._widget.btn_start_r3_user.setEnabled(False)
        self._widget.lbl_connection_status.setText("Connected")

    def stop_r3_user(self):
        if self.r3_thread is not None:
            print('Stop_r3_user')
            self.r3_monitoring.terminate()
            self.r3_monitoring.robot_hostnames.clear()
            self.r3_monitoring.exclude_hostnames = set()
            self.r3_thread.join()
            self.r3_thread = None
            self._widget.btn_stop_r3_user.setEnabled(False)
            self._widget.btn_start_r3_user.setEnabled(True)
            self._widget.lbl_connection_status.setText("Disconnected")
            print('Stop_r3_user done')

    def hostnames_model_item_changed(self):
        print("hostnames_model_item_changed")
        for i in range(self.hostnames_model.rowCount()):
            item = self.hostnames_model.item(i)
            if item.checkState() == Qt.Checked:
                self.r3_monitoring.exclude_hostnames.remove(item.text())
            else:
                self.r3_monitoring.exclude_hostnames.add(item.text())

    def hostnames_model_item_selection_changed(self, index):
        print("hostnames_model_item_selection_changed")
        self.selected_robot_hostname = self.r3_monitoring.robot_hostnames[index.row()]

    def topics_model_item_changed(self):
        print("topics_model_item_changed")
        for i in range(self.topics_model.rowCount()):
            item = self.topics_model.item(i)
            if item.checkState() == Qt.Checked:
                if item.text() in self.r3_monitoring.exclude_topics:
                    self.r3_monitoring.exclude_topics.remove(item.text())
            else:
                self.r3_monitoring.exclude_topics.add(item.text())
                print("remove topic", item.text(), " => skipping messages from this topic")

