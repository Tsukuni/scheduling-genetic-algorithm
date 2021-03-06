# -*- coding: utf-8 -*-
import random
import time
from scoop import futures
from deap import creator, base, tools, algorithms

from organization import Organization
from event import Event
from setting import people_count_sub_sum_weight, not_applicated_count_weight, not_one_assigned_count_weight, applicated_order_count_weight
from shape_input import shape

def setOrganization(line):
  result = []
  for data in line:
    data = data.split(',')
    box_no = int(data.pop(0))
    name = data.pop(0)
    career = int(data.pop(0))
    impossible_time = data
    result.append(Organization(box_no, name, career, impossible_time))
  return result

def evalEvent(individual):
  s = Event(individual, EVENT_BOXES, NEED_PEOPLE, input_path, organization_info)
  s.organizations = organizations
  event_len = len(EVENT_BOXES)
  organizations_number = len(organizations) * event_len

  # 想定人数とアサイン人数の差
  people_count_sub_sum = (1-(sum(s.abs_people_between_need_and_actual()) / organizations_number))
  # 応募していない時間帯へのアサイン数
  not_applicated_count = (1 - (s.not_applicated_assign() / organizations_number))
  # 一つの枠にひとバンドか数える
  not_one_assigned_count = (1 - (event_len - s.only_one_organization_assign()) / event_len)
  # キャリアの長い人を後半へ持ってくる
  #applicated_order_count = s.applicated_order_count()
  return (not_applicated_count, people_count_sub_sum, not_one_assigned_count)

if __name__ == '__main__':
  for a in range(1, 8, 1):
    cross_rate = round(a * 0.1, 1)
    for b in range(1, 8, 1):
      mutation_rate = round(b * 0.1, 1)
      if cross_rate + mutation_rate > 0.9:
        break
      input_no = 1
      for i in range(12):
        start = time.time()
        input_path = 'sample' + str(input_no) + '.txt'
        EVENT_BOXES, NEED_PEOPLE, organization_info = shape(input_path)

        organizations = setOrganization(organization_info)

        creator.create("FitnessPeopleCount", base.Fitness, weights=(not_applicated_count_weight, people_count_sub_sum_weight,
          not_one_assigned_count_weight))
        creator.create("Individual", list, fitness=creator.FitnessPeopleCount)

        toolbox = base.Toolbox()

        toolbox.register("map", futures.map)

        toolbox.register("attr_bool", random.randint, 0, 1)
        toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, len(EVENT_BOXES) * len(organization_info))
        toolbox.register("population", tools.initRepeat, list, toolbox.individual)

        toolbox.register("evaluate", evalEvent)
        # 交叉関数を定義(二点交叉)
        toolbox.register("mate", tools.cxOnePoint)

        # 変異関数を定義(ビット反転、変異隔離が5%ということ?)
        toolbox.register("mutate", tools.mutFlipBit, indpb=0.05)

        # 選択関数を定義(トーナメント選択、tournsizeはトーナメントの数？)
        toolbox.register("select", tools.selTournament, tournsize=3)

        # 初期集団を生成する
        pop = toolbox.population(n=300)
        #1 0.6,0.3 2 0.7 0.2
        CXPB, MUTPB, NGEN = cross_rate, mutation_rate, 1 # 交差確率、突然変異確率、進化計算のループ回数

        print("進化開始")

        # 初期集団の個体を評価する
        fitnesses = list(map(toolbox.evaluate, pop))
        flag = 0
        for ind, fit in zip(pop, fitnesses):  # zipは複数変数の同時ループ
            # 適合性をセットする
            ind.fitness.values = fit

        print(" %i の個体を評価" % len(pop))

          # 進化計算開始
        for g in range(NGEN):
          if (time.time() - start) < 901 :
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
            print("sample" + str(input_no))
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
              if sum(ind.fitness.values) == 0:
                flag = 1
                break
            if flag == 1:
              break
          else:
            break

        print("-- 進化終了 --")

        best_ind = tools.selBest(pop, 1)[0]
        print("最も優れていた個体: %s, %s" % (best_ind, best_ind.fitness.values))
        s = Event(best_ind, EVENT_BOXES, NEED_PEOPLE, input_path, organization_info)
        s.print_csv()
        s.print_tsv()
        elapsed_time = time.time() - start
        s.out_put_result(best_ind.fitness.values, elapsed_time, cross_rate, mutation_rate)
        input_no += 1