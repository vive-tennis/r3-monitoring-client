#ifndef APPCONTROLLER_H
#define APPCONTROLLER_H

#include <QObject>
#include <memory>
#include <QSystemTrayIcon>

#include "form/configurationdialog.h"

class AppController : public QObject
{
    Q_OBJECT
public:
    explicit AppController(QObject *parent = nullptr);
    bool runSystemTray();

private slots:
    void on_topicsAction_triggered();
    void on_accountAction_triggered();
    void on_connectiontAction_triggered();
    void on_aboutAction_triggered();
    void on_quitAction_triggered();

private:
    std::unique_ptr<QSystemTrayIcon> _systemTray;
    std::unique_ptr<ConfigurationDialog> _confDialog;
};

#endif // APPCONTROLLER_H
