# -*- coding: utf-8 -*-
import random
from scoop import futures

from deap import base
from deap import creator
from deap import tools
from deap import cma

from organization import Organization
from event import Event

# 団体定義
e0 = Organization(0, "どこでもOKな人", 10, [])

e1 = Organization(1, "最初ダメな人", 11, ['day1_1','day2_1','day3_1'])

e2 = Organization(2, "真ん中ダメな人", 12, ['day1_2','day2_2','day3_2'])

e3 = Organization(3, "最後ダメな人", 2, ['day3_1','day3_1','day3_1'])

e4 = Organization(4, "どこでもOKな人", 1,[])

e5 = Organization(5, "1日目の最後だけダメな人", 3,['day1_3'])

e6 = Organization(6, "2日目の真ん中ダメな人", 4,['day2_2'])

e7 = Organization(7, "3日目の最初ダメな人", 2, ['day3_1'])

e8 = Organization(8, "1日目の最初しかいけない人", 2, ['day1_2','day1_3',
['day2_1','day2_2','day2_3'],
['day3 _1','day3_2','day3_3']])

organizations = [e0, e1, e2, e3, e4, e5, e6, e7, e8]

creator.create("FitnessPeopleCount", base.Fitness, weights=(-100.0, -100.0, -100.0, -10.0))
creator.create("Individual", list, fitness=creator.FitnessPeopleCount)

toolbox = base.Toolbox()

toolbox.register("map", futures.map)

toolbox.register("attr_bool", random.randint, 0, 1)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, 81)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evalEvent(individual):
  s = Event(individual)
  s.organizations = organizations

  # 想定人数とアサイン人数の差
  people_count_sub_sum = sum(s.abs_people_between_need_and_actual()) / 81.0
  # 応募していない時間帯へのアサイン数
  not_applicated_count = s.not_applicated_assign() / 81.0
  # 一つの枠にひとバンドか数える
  not_one_assigned_count = (9.0 - s.only_one_organization_assign()) / 9.0
  # キャリアの長い人を後半へ持ってくる
  applicated_order_count = s.applicated_order_count()
  return (not_applicated_count, people_count_sub_sum, not_one_assigned_count, applicated_order_count)

toolbox.register("evaluate", evalEvent)
# 交叉関数を定義(二点交叉)
toolbox.register("mate", tools.cxTwoPoint)

# 変異関数を定義(ビット反転、変異隔離が5%ということ?)
toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)

# 選択関数を定義(トーナメント選択、tournsizeはトーナメントの数？)
toolbox.register("select", tools.selTournament, tournsize=3)

if __name__ == '__main__':
    # 初期集団を生成する
    pop = toolbox.population(n=300)
    CXPB, MUTPB, NGEN = 0.6, 0.05, 1000 # 交差確率、突然変異確率、進化計算のループ回数

    print("進化開始")

    # 初期集団の個体を評価する
    fitnesses = list(map(toolbox.evaluate, pop))
    for ind, fit in zip(pop, fitnesses):  # zipは複数変数の同時ループ
        # 適合性をセットする
        ind.fitness.values = fit

    print(" %i の個体を評価" % len(pop))

     # 進化計算開始
    for g in range(NGEN):
        print("-- %i 世代 --" % g)

        # 選択
        # 次世代の個体群を選択
        offspring = toolbox.select(pop, len(pop))
        # 個体群のクローンを生成
        offspring = list(map(toolbox.clone, offspring))

        # 選択した個体群に交差と突然変異を適応する
        # 交叉
        # 偶数番目と奇数番目の個体を取り出して交差
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < CXPB:
                toolbox.mate(child1, child2)
                # 交叉された個体の適合度を削除する
                del child1.fitness.values
                del child2.fitness.values

        # 変異
        for mutant in offspring:
            if random.random() < MUTPB:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # 適合度が計算されていない個体を集めて適合度を計算
        invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
        fitnesses = map(toolbox.evaluate, invalid_ind)
        for ind, fit in zip(invalid_ind, fitnesses):
            ind.fitness.values = fit

        print("  %i の個体を評価" % len(invalid_ind))

        # 次世代群をoffspringにする
        pop[:] = offspring

        # すべての個体の適合度を配列にする
        index = 1
        for v in ind.fitness.values:
          fits = [v for ind in pop]

          length = len(pop)
          mean = sum(fits) / length
          sum2 = sum(x*x for x in fits)
          std = abs(sum2 / length - mean**2)**0.5

          print("* パラメータ%d" % index)
          print("  Min %s" % min(fits))
          print("  Max %s" % max(fits))
          print("  Avg %s" % mean)
          print("  Std %s" % std)
          index += 1

    print("-- 進化終了 --")

    best_ind = tools.selBest(pop, 1)[0]
    print("最も優れていた個体: %s, %s" % (best_ind, best_ind.fitness.values))
    s = Event(best_ind)
    s.print_csv()
    s.print_tsv()