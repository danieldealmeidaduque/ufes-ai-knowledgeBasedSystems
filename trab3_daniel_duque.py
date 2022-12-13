from scipy import stats
from scipy.stats import wilcoxon
from scipy.stats import ttest_rel as t_test
from matplotlib import pyplot as plt
import seaborn as sns
from click import UsageError
import numpy as np
import pandas as pd
import pygame
import os
import random
import time
from sys import exit
from experta import *

pygame.init()

# Valid values: HUMAN_MODE or AI_MODE
GAME_MODE = "AI_MODE"

GRAF = False

# Global Constants
SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100
if(GRAF):
    SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

RUNNING = [pygame.image.load(os.path.join("Assets/Dino", "DinoRun1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoRun2.png"))]
JUMPING = pygame.image.load(os.path.join("Assets/Dino", "DinoJump.png"))
DUCKING = [pygame.image.load(os.path.join("Assets/Dino", "DinoDuck1.png")),
           pygame.image.load(os.path.join("Assets/Dino", "DinoDuck2.png"))]

SMALL_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus1.png")),
                pygame.image.load(os.path.join(
                    "Assets/Cactus", "SmallCactus2.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "SmallCactus3.png"))]
LARGE_CACTUS = [pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus1.png")),
                pygame.image.load(os.path.join(
                    "Assets/Cactus", "LargeCactus2.png")),
                pygame.image.load(os.path.join(
                    "Assets/Cactus", "LargeCactus3.png")),
                pygame.image.load(os.path.join("Assets/Cactus", "LargeCactus4.png"))]

BIRD = [pygame.image.load(os.path.join("Assets/Bird", "Bird1.png")),
        pygame.image.load(os.path.join("Assets/Bird", "Bird2.png"))]

CLOUD = pygame.image.load(os.path.join("Assets/Other", "Cloud.png"))

BG = pygame.image.load(os.path.join("Assets/Other", "Track.png"))


class Dinosaur:
    X_POS = 90
    Y_POS = 330
    Y_POS_DUCK = 355
    JUMP_VEL = 17
    JUMP_GRAV = 1.1

    def __init__(self):
        self.duck_img = DUCKING
        self.run_img = RUNNING
        self.jump_img = JUMPING

        self.dino_duck = False
        self.dino_run = True
        self.dino_jump = False

        self.step_index = 0
        self.jump_vel = 0
        self.jump_grav = self.JUMP_VEL
        self.image = self.run_img[0]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS

    def update(self, userInput):
        if self.dino_duck and not self.dino_jump:
            self.duck()
        if self.dino_run:
            self.run()
        if self.dino_jump:
            self.jump()

        if self.step_index >= 20:
            self.step_index = 0

        if userInput == "K_UP" and not self.dino_jump:
            self.dino_duck = False
            self.dino_run = False
            self.dino_jump = True
        elif userInput == "K_DOWN" and not self.dino_jump:
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = False
        elif userInput == "K_DOWN":
            self.dino_duck = True
            self.dino_run = False
            self.dino_jump = True
        elif not (self.dino_jump or userInput == "K_DOWN"):
            self.dino_duck = False
            self.dino_run = True
            self.dino_jump = False

    def duck(self):
        self.image = self.duck_img[self.step_index // 10]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS_DUCK
        self.step_index += 1

    def run(self):
        self.image = self.run_img[self.step_index // 10]
        self.dino_rect = self.image.get_rect()
        self.dino_rect.x = self.X_POS
        self.dino_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.dino_duck:
            self.jump_grav = self.JUMP_GRAV * 4
        if self.dino_jump:
            self.dino_rect.y -= self.jump_vel
            self.jump_vel -= self.jump_grav
        if self.dino_rect.y > self.Y_POS + 10:
            self.dino_jump = False
            self.jump_vel = self.JUMP_VEL
            self.jump_grav = self.JUMP_GRAV
            self.dino_rect.y = self.Y_POS
    if(GRAF):
        def draw(self, SCREEN):
            SCREEN.blit(self.image, (self.dino_rect.x, self.dino_rect.y))

    def getXY(self):
        return (self.dino_rect.x, self.dino_rect.y)


class Cloud:
    def __init__(self):
        self.x = SCREEN_WIDTH + random.randint(800, 1000)
        self.y = random.randint(50, 100)
        self.image = CLOUD
        self.width = self.image.get_width()

    def update(self):
        self.x -= game_speed
        if self.x < -self.width:
            self.x = SCREEN_WIDTH + random.randint(2500, 3000)
            self.y = random.randint(50, 100)

    if(GRAF):
        def draw(self, SCREEN):
            SCREEN.blit(self.image, (self.x, self.y))


class Obstacle():
    def __init__(self, image, type):
        super().__init__()
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()

        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < - self.rect.width:
            obstacles.pop(0)

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)

    def getXY(self):
        return (self.rect.x, self.rect.y)

    def getHeight(self):
        return y_pos_bg - self.rect.y

    def getType(self):
        return (self.type)


class SmallCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 345


class LargeCactus(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 325


class Bird(Obstacle):
    def __init__(self, image):
        self.type = 0
        super().__init__(image, self.type)

        # High, middle or ground
        if random.randint(0, 3) == 0:
            self.rect.y = 345
        elif random.randint(0, 2) == 0:
            self.rect.y = 260
        else:
            self.rect.y = 300
        self.index = 0

    def draw(self, SCREEN):
        if self.index >= 19:
            self.index = 0
        SCREEN.blit(self.image[self.index // 10], self.rect)
        self.index += 1


class KeyClassifier:
    def __init__(self, state):
        pass

    def keySelector(self, distance, obHeight, speed, obType):
        pass

    def updateState(self, state):
        pass


"""
def first(x):
    return x[0]
"""


class RuleBasedPlayer(KnowledgeEngine):

    def setAction(self, action):
        self.action = action

    def getAction(self):
        return self.action

    # ADICIONEI
    @Rule(AND(Fact(speed=P(lambda x: x <= 11)),
              Fact(distance=P(lambda x: x < 250)),
              NOT(Fact(action='K_DOWN'))))
    def jumpVerySlow(self):
        self.retract(1)
        self.declare(Fact(action='K_UP'))

    # MODIFIQUEI
    @Rule(AND(Fact(speed=P(lambda x: x > 11 and x < 15)),
              Fact(distance=P(lambda x: x < 300)),
              NOT(Fact(action='K_DOWN'))))
    def jumpSlow(self):
        self.retract(1)
        self.declare(Fact(action='K_UP'))

    @Rule(AND(Fact(speed=P(lambda x: x >= 15 and x < 17)),
              Fact(distance=P(lambda x: x < 400)),
              NOT(Fact(action='K_DOWN'))))
    def jumpFast(self):
        self.retract(1)
        self.declare(Fact(action='K_UP'))

    # MODIFIQUEI
    @Rule(AND(Fact(speed=P(lambda x: x >= 17 and x < 20)),
              Fact(distance=P(lambda x: x < 500)),
              NOT(Fact(action='K_DOWN'))))
    def jumpVeryFast(self):
        self.retract(1)
        self.declare(Fact(action='K_UP'))

    # ADICIONEI
    @Rule(AND(Fact(speed=P(lambda x: x >= 20 and x < 22)),
              Fact(distance=P(lambda x: x < 600)),
              NOT(Fact(action='K_DOWN'))))
    def jumpVeryFast_2(self):
        self.retract(1)
        self.declare(Fact(action='K_UP'))

    # ADICIONEI
    @Rule(AND(Fact(speed=P(lambda x: x >= 22)),
              Fact(distance=P(lambda x: x < 650)),
              NOT(Fact(action='K_DOWN'))))
    def jumpVeryFast_3(self):
        self.retract(1)
        self.declare(Fact(action='K_UP'))

    @Rule(AND(Fact(obType=P(lambda x: isinstance(x, Bird))),
              Fact(obHeight=P(lambda x: x > 50))))
    def getDown(self):
        self.retract(1)
        self.declare(Fact(action='K_DOWN'))

    @Rule(Fact(action=MATCH.action))
    def selectAction(self, action):
        self.setAction(action)


class RuleBasedKeyClassifier(KeyClassifier):
    def __init__(self):
        self.engine = RuleBasedPlayer()

    def keySelector(self, dist, obH, sp, obT):
        self.engine.reset()
        self.engine.declare(Fact(action='K_NO'))
        self.engine.declare(Fact(distance=dist))
        self.engine.declare(Fact(obHeight=obH))
        self.engine.declare(Fact(speed=sp))
        self.engine.declare(Fact(obType=obT))
        self.engine.run()
        return self.engine.getAction()


def playerKeySelector():
    userInputArray = pygame.key.get_pressed()

    if userInputArray[pygame.K_UP]:
        return "K_UP"
    elif userInputArray[pygame.K_DOWN]:
        return "K_DOWN"
    else:
        return "K_NO"


def playGame():
    global game_speed, x_pos_bg, y_pos_bg, points, obstacles
    run = True
    # clock = pygame.time.Clock()
    player = Dinosaur()
    cloud = Cloud()
    game_speed = 10
    x_pos_bg = 0
    y_pos_bg = 383
    points = 0
    font = pygame.font.Font('freesansbold.ttf', 20)
    obstacles = []
    death_count = 0
    spawn_dist = 0

    def score():
        global points, game_speed
        points += 0.25
        if points % 100 == 0:
            game_speed += 1

        text = font.render("Points: " + str(int(points)), True, (0, 0, 0))
        textRect = text.get_rect()
        textRect.center = (1000, 40)
        if(GRAF):
            SCREEN.blit(text, textRect)

    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        if(GRAF):
            SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
            SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            if(GRAF):
                SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
            x_pos_bg = 0
        x_pos_bg -= game_speed

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                exit()

        if(GRAF):
            SCREEN.fill((255, 255, 255))

        distance = 1500
        obHeight = 0
        obType = 2
        if len(obstacles) != 0:
            xy = obstacles[0].getXY()
            distance = xy[0]
            obHeight = obstacles[0].getHeight()
            obType = obstacles[0]

        if GAME_MODE == "HUMAN_MODE":
            userInput = playerKeySelector()
        else:
            userInput = aiPlayer.keySelector(
                distance, obHeight, game_speed, obType)

        if len(obstacles) == 0 or obstacles[-1].getXY()[0] < spawn_dist:
            spawn_dist = random.randint(0, 670)
            if random.randint(0, 2) == 0:
                obstacles.append(SmallCactus(SMALL_CACTUS))
            elif random.randint(0, 2) == 1:
                obstacles.append(LargeCactus(LARGE_CACTUS))
            elif random.randint(0, 5) == 5:
                obstacles.append(Bird(BIRD))

        player.update(userInput)
        if(GRAF):
            player.draw(SCREEN)

        for obstacle in list(obstacles):
            obstacle.update()
            if(GRAF):
                obstacle.draw(SCREEN)

        background()

        if(GRAF):
            cloud.draw(SCREEN)
        cloud.update()

        score()

        # clock.tick(60)
        if(GRAF):
            pygame.display.update()

        for obstacle in obstacles:
            if player.dino_rect.colliderect(obstacle.rect):
                print(
                    f'{points} - userInput: {userInput} - game_speed: {game_speed} - distance: {distance} - obHeight: {obHeight}')
                # print(points)
                # pygame.time.delay(2000)
                death_count += 1

                return points


def manyPlaysResults(rounds):
    # print(f'Playing {rounds} rounds...\n')
    results = []
    for round in range(rounds):
        results += [playGame()]
    npResults = np.asarray(results)
    return (results, npResults.mean() - npResults.std())


confiance_interval = 0.95  # 95%
alpha = 1 - confiance_interval  # 5%


def results_accuracy(scores):
    mean = scores.mean()
    std = scores.std()
    inf, sup = stats.norm.interval(confiance_interval,
                                   loc=mean,
                                   scale=std/np.sqrt(len(scores)))

    return {'media': mean,
            'desvio_padrao': std,
            'limite_inferior': inf,
            'limite_superior': sup}


def table_accuracy(scores):
    d = {k: results_accuracy(v) for k, v in scores.items()}
    df = pd.DataFrame(d).T
    # arredonda os valores para 2 casas decimais
    df = df.applymap(lambda x: f'{x:.2f}')

    return df


def results_paired(scores1, scores2):
    _, p_value_t = t_test(scores1, scores2)
    _, p_value_w = wilcoxon(scores1, scores2)

    return p_value_t, p_value_w


def table_paired(scores):
    # lista as keys para facilitar manipulacao
    keys = list(scores.keys())
    # quantidade de keys para criar tamanho da matriz
    size = len(keys)
    # matrix que eh a tabela pareada
    matrix_hyp = np.zeros((size, size))

    # faz a tabela pareada
    for i in range(size):
        k1 = keys[i]
        s1 = scores[k1]
        for j in range(size):
            k2 = keys[j]
            s2 = scores[k2]
            # diagonal vai ficar o nome do classificador
            if k1 == k2:
                matrix_hyp[i][j] = np.NaN
            # nao diagonal vai ficar os p-values dos testes pareados
            else:
                t, w = results_paired(s1, s2)
                # triangular superior = p-value do t-pareado
                matrix_hyp[i][j] = t
                # triangular inferior = p-value do wilcoxon
                matrix_hyp[j][i] = w

        # transforma a matriz em um dataframe para facilitar manipulacao
        df = pd.DataFrame(matrix_hyp, index=scores, columns=scores)
        # arredonda os valores para 3 casas decimais
        df = df.applymap(lambda x: f'{x:.3e}' if x < 0.0001 else f'{x:.3f}')
        # transforma os valores para string para poder manipular
        df = df.astype(str)
        # coloca a diagonal do dataframe com os respectivos nomes dos classificadores
        df.at['DUQUE_REFORCO', 'DUQUE_REFORCO'] = 'DUQUE_REFORCO'
        df.at['VAREJAO_REFORCO', 'VAREJAO_REFORCO'] = 'VAREJAO_REFORCO'
        df.at['DUQUE_SBC', 'DUQUE_SBC'] = 'DUQUE_SBC'
        df.at['VAREJAO_SBC', 'VAREJAO_SBC'] = 'VAREJAO_SBC'

        # coloca em negrito quando p-value < 0.05
        def apply_bold(txt):
            try:
                bold = 'bold' if float(txt) < alpha else ''
                return 'font-weight: %s' % bold
            except:
                None

        # aplica o negrito no estilo do dataframe
        df_style = df.style.applymap(apply_bold)

        return df, df_style


def main():
    global aiPlayer
    # start = time.process_time()

    # aiPlayer = RuleBasedKeyClassifier()
    # # print(playGame())
    # res, value = manyPlaysResults(30)
    # npRes = np.asarray(res)

    # end = time.process_time()

    # print(f'{res}\n{npRes.mean()}\n{npRes.std()}\n{value}\n')
    # print(f'Ended in {round(end - start,2)} s')

    # file = open('rule_based_results.txt', 'w')
    # file.write(
    #     f'{res}\n\nMean: {npRes.mean()}\nStd: {npRes.std()}\n')
    # file.write(f'Value: {value}\n\nEnded in {round(end - start,2)} s')
    # file.close()

    # abaixo esta a parte só pra gerar a tabela pareada e o boxplot usados no artigo

    # SCORES
    duque_reforco_scores = [1547.25, 51.0, 302.5, 446.75, 607.75, 58.75, 50.25, 159.75, 1819.5, 1661.75, 23.25,
                            100.25, 693.0, 1823.25, 571.5, 100.5, 499.25, 1528.0, 588.75, 245.5, 503.75, 60.75,
                            37.25, 539.5, 286.5, 1007.5, 258.5, 236.5, 425.25, 83.5]

    varejao_reforco_scores = [1214.0, 759.5, 1164.25, 977.25, 1201.0, 930.0, 1427.75, 799.5, 1006.25, 783.5,
                              728.5, 419.25, 1389.5, 730.0, 1306.25, 675.5, 1359.5, 1000.25, 1284.5, 1350.0,
                              751.0, 1418.75, 1276.5, 1645.75, 860.0, 745.5, 1426.25, 783.5, 1149.75, 1482.25]

    duque_sbc_scores = [1508.0, 1699.0, 1142.0, 1155.5, 1229.75, 1020.0, 1307.0, 1210.5, 919.5,
                        1309.0, 886.0, 1316.25, 1258.25, 1073.0, 1547.5, 1619.75, 1494.0, 1429.25,
                        1118.0, 1130.75, 1350.25, 1000.25, 1582.5, 924.0, 1437.5, 1548.5, 1142.75,
                        1016.5, 1531.5, 1032.5]

    varejao_sbc_scores = [113.25, 1288.0, 1254.5, 1201.0, 1107.25, 1192.5, 1379.5, 1515.0, 191.5,
                          830.25, 1233.5, 955.75, 1402.25, 1051.75, 72.75, 1128.75, 1248.5, 1103.25,
                          975.75, 895.0, 1337.0, 1051.25, 1271.5, 1432.75, 106.75, 1231.75, 80.0,
                          1236.5, 1414.75, 1363.0]

    dict_scores = {'DUQUE_REFORCO': np.array(duque_reforco_scores),
                   'VAREJAO_REFORCO': np.array(varejao_reforco_scores),
                   'DUQUE_SBC': np.array(duque_sbc_scores),
                   'VAREJAO_SBC': np.array(varejao_sbc_scores)}

    df = pd.DataFrame(dict_scores)

    # 1
    df_acc = table_accuracy(dict_scores)
    with pd.ExcelWriter('accuracy_table.xlsx') as writer:
        df_acc.to_excel(writer, sheet_name='sheet_1')

    # 2
    fig, axes = plt.subplots(figsize=(7, 7))
    sns.boxplot(data=df.loc[:, :])
    axes.set_xlabel('Classificador')
    axes.set_ylabel('Acurracy Score')
    plt.savefig('accuracy_boxplot.pdf')

    # 3
    df_paired, df_style_paired = table_paired(dict_scores)

    with pd.ExcelWriter('paired_table.xlsx') as writer:
        df_paired.to_excel(writer, sheet_name='sheet_1')


main()
