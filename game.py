import random
from PyQt5.QtWidgets import QRadioButton, QDialog, QLabel, QProgressBar, QApplication, QMainWindow, QSizePolicy,\
    QPushButton, QVBoxLayout, QWidget
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
import sys
import os
import yaml

with open("drugs.yml") as f:
    drugs = yaml.safe_load(f)

groups = list(drugs.keys())


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        self.mainWidget = QWidget(self)
        self.questionWidget = QDialog(self)
        self.questionLayout = QVBoxLayout()
        self.questionWidget.setLayout(self.questionLayout)

        self.layout = QVBoxLayout()
        self.answers = QVBoxLayout()
        self.answersWidget = QWidget()
        self.answersWidget.setLayout(self.answers)

        self.question = QLabel('')
        newfont = QFont("Arial", 30, QFont.Bold)
        self.question.setFont(newfont)
        self.question.setWordWrap(True)
        self.question.setMaximumWidth(2000)
        self.question.setSizePolicy(QSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding))

        self.questionLayout.addWidget(self.question)

        self.questionLayout.addWidget(self.answersWidget)

        self.mainWidget.setLayout(self.layout)
        self.setCentralWidget(self.mainWidget)
        self.show()

        self.answerWidget = QWidget()
        self.answerLayout = QVBoxLayout()

        self.answerWidget.setLayout(self.answerLayout)

        self.answerPicture = QLabel()
        self.answerLayout.addWidget(self.answerPicture)

        self.result = QLabel()
        self.answer_screen_confirm = QPushButton(text='OK')
        self.answerLayout.addWidget(self.result)
        self.answerLayout.addWidget(self.answer_screen_confirm)
        self.answer_screen_confirm.clicked.connect(self.ask_question)

        self.scoreWidget = QLabel()
        self.scoreWidget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum))
        self.layout.addWidget(self.scoreWidget)
        self.total_correct = 0
        self.total_answered = 0

        self.progressWidget = QProgressBar()
        self.progressWidget.setSizePolicy(QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum))
        self.progressWidget.setMaximum(sum([len(drugs[group]) for group in groups]))
        self.progressWidget.setValue(0)

        self.layout.addWidget(self.progressWidget)

        self.question_confirm = QPushButton(text='OK')
        self.questionLayout.addWidget(self.question_confirm)
        self.layout.addWidget(self.questionWidget)
        self.layout.addWidget(self.answerWidget)
        self.question_confirm.clicked.connect(self.check_answer)
        self.resize(500, 200)

        self.answer_buttons = [QRadioButton() for _ in range(3)]
        for button in self.answer_buttons:
            self.answers.addWidget(button)

        self.drugs = dict(drugs)
        self.groups = list(groups)

        self.previous = 'drug'
        self.ask_question()

    def ask_question(self):

        if self.previous == 'group':
            self.question_drug()
        else:
            random.choice([self.question_group, self.question_description])()

    def question_drug(self):
        self.answerWidget.hide()
        self.questionWidget.show()

        group_answers = list(self.drugs[self.group].values())
        options = list(range(3))
        random.shuffle(options)
        self.answer_text = self.drugs[self.group][self.drug]

        self.answer = options.pop()

        wrong_answers = list(group_answers)
        wrong_answers.remove(self.drugs[self.group][self.drug])
        random.shuffle(wrong_answers)

        possible_answers: list = [None] * 3

        possible_answers[self.answer] = self.drugs[self.group][self.drug]

        if len(wrong_answers) > 0:
            possible_answers[options.pop()] = wrong_answers.pop()
        else:
            possible_answers[options.pop()] = ''

        self.question.setText('What is {}?'.format(self.drug))

        for i, possible_answer in enumerate(possible_answers):
            self.answer_buttons[i].setText(possible_answers[i])

        self.previous = 'drug'

        # self.resize(self.Layout.sizeHint())

    def question_group(self):
        if sum([len(self.drugs[group]) for group in self.groups]) == 0:

            self.result.setText('Well done, you completed all the drugs!')
            self.questionWidget.hide()
            self.answerWidget.show()
            self.answer_screen_confirm.hide()
            return


        self.answerWidget.hide()
        self.questionWidget.show()

        self.update_answer()
        options = list(range(3))
        random.shuffle(options)

        self.answer = options.pop()

        self.answer_text = self.group

        wrong_answers = list(self.groups)
        wrong_answers.remove(self.group)
        random.shuffle(wrong_answers)

        possible_answers: list = [None] * 3

        possible_answers[self.answer] = self.group
        if len(wrong_answers) > 0:
            possible_answers[options.pop()] = wrong_answers.pop()
        else:
            possible_answers[options.pop()] = ''
        if len(wrong_answers) > 0:
            possible_answers[options.pop()] = wrong_answers.pop()
        else:
            possible_answers[options.pop()] = ''

        self.question.setText('What group is {} in?'.format(self.drug))

        for i, possible_answer in enumerate(possible_answers):
            self.answer_buttons[i].setText(possible_answers[i])

        self.previous = 'group'

    def question_description(self):
        self.answerWidget.hide()
        self.questionWidget.show()

        self.update_answer()
        options = list(range(3))
        random.shuffle(options)
        self.answer_text = self.drug
        self.questionText = self.drugs[self.group][self.drug]

        self.answer = options.pop()
        group_answers = list(self.drugs[self.group].keys())

        wrong_answers = list(group_answers)
        wrong_answers.remove(self.drug)
        random.shuffle(wrong_answers)

        possible_answers: list = [None] * 3

        possible_answers[self.answer] = self.drug
        if len(wrong_answers) > 0:
            possible_answers[options.pop()] = wrong_answers.pop()
        else:
            possible_answers[options.pop()] = ''
        if len(wrong_answers) > 0:
            possible_answers[options.pop()] = wrong_answers.pop()
        else:
            possible_answers[options.pop()] = ''

        self.question.setText('What is {}?'.format(self.drugs[self.group][self.drug]))

        for i, possible_answer in enumerate(possible_answers):
            self.answer_buttons[i].setText(possible_answers[i])

        self.previous = 'description'

    def update_answer(self):
        self.group = random.choice(self.groups)
        group_drugs = list(self.drugs[self.group].keys())
        self.drug = random.choice(group_drugs)
        self.questionText = self.drug

    def check_answer(self):
        for i, a in enumerate(self.answer_buttons):

            if a.isChecked():
                if i == self.answer:
                    self.result.setText('Correct! \n\n{} is {}'.format(self.questionText, self.answer_text))
                    self.answerPicture.setPixmap(QPixmap(
                        random.choice([os.path.join('images', image) for image in os.listdir('images')
                                       if 'chicken' in image])).scaledToHeight(200))
                    self.total_correct += 1

                    if self.previous != 'group':
                        self.drugs[self.group].pop(self.drug)
                        self.progressWidget.setValue(self.progressWidget.value() + 1)

                    if len(self.drugs[self.group]) == 0:
                        self.groups.remove(self.group)
                else:
                    self.result.setText('Wrong!\n\n{} is actually {}'.format(self.questionText, self.answer_text))
                    self.answerPicture.setPixmap(QPixmap(
                        random.choice([os.path.join('images', image) for image in os.listdir('images')
                                       if 'rooster' in image])
                    ).scaledToHeight(200))
                break

        self.answerPicture.setAlignment(Qt.AlignCenter)

        self.total_answered += 1

        self.scoreWidget.setText('{} out of {} correct so far, {} drugs remaining'.format(
            self.total_correct, self.total_answered, sum([len(self.drugs[group]) for group in self.groups])))
        self.questionWidget.hide()
        self.answerWidget.show()
        # self.resize(self.questionLayout.sizeHint())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())