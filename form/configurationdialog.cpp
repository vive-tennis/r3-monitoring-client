#include "configurationdialog.h"
#include "ui_configurationdialog.h"

#include <QCheckBox>
#include <QLabel>

ConfigurationDialog::ConfigurationDialog(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::ConfigurationDialog)
{
    ui->setupUi(this);
}

ConfigurationDialog::~ConfigurationDialog()
{
    delete ui;
}

void ConfigurationDialog::setTopicList(QList<Topic> topicList)
{
    _topicList = topicList;

    // create widgets;
    for (int i = 0; i < _topicList.size(); ++i) {
        const auto &topic = _topicList[i];

        QCheckBox *cbName = new QCheckBox(ui->TopicsWidget);
        cbName->setText(topic.name);
        cbName->setChecked(topic.excluded);
        ui->topicGridLayout->addWidget(cbName, i, 0);

        QLabel *lblType = new QLabel(ui->TopicsWidget);
        lblType->setText(topic.type);
        ui->topicGridLayout->addWidget(lblType, i, 1);

        QLabel *lblDate = new QLabel(ui->TopicsWidget);
        lblDate->setText(topic.time_created);
        ui->topicGridLayout->addWidget(lblDate, i, 2);
    }
}

void ConfigurationDialog::setTab(TabName tabName)
{
    switch (tabName) {
    case TabName::TOPICS:
        ui->tabWidget->setCurrentWidget(ui->TopicsWidget);
        break;
    case TabName::ACCOUNT:
        ui->tabWidget->setCurrentWidget(ui->AccountWidget);
        break;
    case TabName::CONNECTION:
        ui->tabWidget->setCurrentWidget(ui->ConnectionWidget);
        break;
    case TabName::ABOUT:
        ui->tabWidget->setCurrentWidget(ui->AboutWidget);
        break;
    default:
        break;
    }
}
