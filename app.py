import random
from PyQt5.QtWidgets import QRadioButton, QDialog, QLabel, QProgressBar, QApplication, QMainWindow, QSizePolicy, \
    QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
import sys
import os
import yaml


def get_path(filename):
    try:
        return os.path.join(sys._MEIPASS, filename)
    except AttributeError:
        return os.path.join('.', filename)


images = get_path('images')
images = [os.path.join(images, image) for image in os.listdir(images)]

with open(get_path("drugs.yml")) as f:
    drugs = yaml.safe_load(f)

groups = list(drugs.keys())


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mainWidget = QWidget(self)
        self.mainLayout = QVBoxLayout()
        self.mainWidget.setLayout(self.mainLayout)
        self.setCentralWidget(self.mainWidget)

        self.questionLayout = QVBoxLayout()
        self.questionWidget = QDialog(self)
        self.questionWidget.setLayout(self.questionLayout)
        self.questionLabel = QLabel('')
        self.questionLabel.setFont(QFont("Arial", 30, QFont.Bold))
        self.questionLabel.setWordWrap(True)
        self.questionLabel.setMaximumWidth(2000)
        self.questionLabel.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding))
        self.questionLayout.addWidget(self.questionLabel)
        self.mainLayout.addWidget(self.questionWidget)

        self.choicesLayout = QVBoxLayout()
        self.choicesWidget = QWidget()
        self.choicesWidget.setLayout(self.choicesLayout)
        self.questionLayout.addWidget(self.choicesWidget)

        self.show()

        self.answerWidget = QWidget()
        self.answerLayout = QVBoxLayout()
        self.answerWidget.setLayout(self.answerLayout)

        self.answerPicture = QLabel()
        self.answerLayout.addWidget(self.answerPicture)

        self.resultLabel = QLabel()
        self.resultLabel.setFont(QFont("Arial", 15))
        self.resultTitleLabel = QLabel()
        self.resultTitleLabel.setFont(QFont("Arial", 20, QFont.Bold))
        self.answer_screen_confirm = QPushButton(text='OK')
        self.answerLayout.addWidget(self.resultTitleLabel)
        self.answerLayout.addWidget(self.resultLabel)
        self.answerLayout.addWidget(self.answer_screen_confirm)
        # noinspection PyUnresolvedReferences
        self.answer_screen_confirm.clicked.connect(self.ask_question)

        self.scoreWidget = QLabel()
        self.scoreWidget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum))
        self.mainLayout.addWidget(self.scoreWidget)
        self.total_correct = 0
        self.total_answered = 0

        self.progressWidget = QProgressBar()
        self.progressWidget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum))
        self.progressWidget.setMaximum(sum([len(drugs[group]) for group in groups]))
        self.progressWidget.setValue(0)

        self.mainLayout.addWidget(self.progressWidget)

        self.question_confirm = QPushButton(text='OK')
        self.questionLayout.addWidget(self.question_confirm)
        self.mainLayout.addWidget(self.questionWidget)
        self.mainLayout.addWidget(self.answerWidget)
        # noinspection PyUnresolvedReferences
        self.question_confirm.clicked.connect(self.check_answer)
        self.resize(500, 200)

        self.answer_buttons = [QRadioButton() for _ in range(3)]
        for button in self.answer_buttons:
            button.setFont(QFont("Arial", 15))
            self.choicesLayout.addWidget(button)

        self.answer_idx = None

        self.question = None
        self.answer = None

        self.drug = None
        self.group = None

        self.previous = 'drug'
        self.ask_question()

    def ask_question(self):

        if sum([len(drugs[group]) for group in groups]) == 0:
            self.resultTitleLabel.setText('Well done!')
            self.resultLabel.setText("You got {} out of {} correct ({} %).".format(
                self.total_correct, self.total_answered, self.total_correct / self.total_answered * 100))
            self.questionLabel.hide()
            self.answerWidget.show()
            self.answer_screen_confirm.hide()
            return

        if self.previous == 'group':
            self.question_drug()
        else:
            random.choice([self.question_group, self.question_description])()

    def question_drug(self):
        self.answerWidget.hide()
        self.questionWidget.show()

        self.question = self.drug
        self.answer = drugs[self.group][self.drug]

        choices = self.generate_choices(drugs[self.group].values())

        self.questionLabel.setText('What is {}?'.format(self.drug))

        for i, possible_answer in enumerate(choices):
            self.answer_buttons[i].setText(choices[i])

        self.previous = 'drug'

        # self.resize(self.Layout.sizeHint())

    def question_group(self):

        self.answerWidget.hide()
        self.questionWidget.show()

        self.update_answer()

        self.question = self.drug
        self.answer = self.group

        choices = self.generate_choices(groups)

        self.questionLabel.setText('What group is {} in?'.format(self.drug))

        for i, possible_answer in enumerate(choices):
            self.answer_buttons[i].setText(choices[i])

        self.previous = 'group'

    def question_description(self):
        self.answerWidget.hide()
        self.questionWidget.show()

        self.update_answer()

        self.question = drugs[self.group][self.drug]
        self.answer = self.drug

        choices = self.generate_choices(drugs[self.group].keys())

        self.questionLabel.setText('What drug fits the description: "{}"'.format(self.question))

        for i, possible_answer in enumerate(choices):
            self.answer_buttons[i].setText(choices[i])

        self.previous = 'description'

    def update_answer(self):
        self.group = random.choice(groups)
        group_drugs = list(drugs[self.group].keys())
        self.drug = random.choice(group_drugs)

    def check_answer(self):
        for i, a in enumerate(self.answer_buttons):

            if a.isChecked():
                if i == self.answer_idx:
                    self.resultTitleLabel.setText('Correct!')
                    self.resultLabel.setText('{} is {}'.format(self.question, self.answer))
                    self.answerPicture.setPixmap(QPixmap(
                        random.choice([image for image in images if 'chicken' in os.path.basename(image)])
                    ).scaledToHeight(200))
                    self.total_correct += 1

                    if self.previous != 'group':
                        drugs[self.group].pop(self.drug)
                        self.progressWidget.setValue(self.progressWidget.value() + 1)

                    if len(drugs[self.group]) == 0:
                        groups.remove(self.group)
                else:
                    self.resultTitleLabel.setText('Wrong!')
                    self.resultLabel.setText('{} is actually {}{}'.format(self.question,
                                                                          'in ' if self.previous == 'group' else '',
                                                                          self.answer))
                    self.answerPicture.setPixmap(QPixmap(
                        random.choice([image for image in images if 'rooster' in os.path.basename(image)])
                    ).scaledToHeight(200))
                break

        self.answerPicture.setAlignment(Qt.AlignCenter)

        self.total_answered += 1

        self.scoreWidget.setText('{} out of {} correct so far, {} drugs remaining'.format(
            self.total_correct, self.total_answered, sum([len(drugs[group]) for group in groups])))
        self.questionWidget.hide()
        self.answerWidget.show()
        # self.resize(self.questionLayout.sizeHint())

    def generate_choices(self, possible_answers):
        options = list(range(3))
        random.shuffle(options)

        self.answer_idx = options.pop()
        self.answer_buttons[self.answer_idx].show()

        wrong_answers = list(possible_answers)
        wrong_answers.remove(self.answer)
        random.shuffle(wrong_answers)

        choices: list = [None] * 3

        choices[self.answer_idx] = self.answer
        for idx in options:
            if len(wrong_answers) > 0:
                choices[idx] = wrong_answers.pop()
                self.answer_buttons[idx].show()
            else:
                self.answer_buttons[idx].hide()

        return choices


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
