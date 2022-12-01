#ifndef CONFIGURATIONDIALOG_H
#define CONFIGURATIONDIALOG_H

#include <QDialog>

namespace Ui {
class ConfigurationDialog;
}

class ConfigurationDialog : public QDialog
{
    Q_OBJECT

public:
    enum class TabName {
        TOPICS,
        ACCOUNT,
        CONNECTION,
        ABOUT
    };

public:
    explicit ConfigurationDialog(QWidget *parent = nullptr);
    ~ConfigurationDialog();
    void setTab(TabName tabName);

private:
    Ui::ConfigurationDialog *ui;
    TabName _tabName;
};

#endif // CONFIGURATIONDIALOG_H
