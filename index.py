# -*- coding: utf-8 -*-
import random
from scoop import futures

from deap import base
from deap import creator
from deap import tools
from deap import cma

# 団体を表すクラス
class Organization(object):
  def __init__(self, no, name, career, impossible_time):
    self.no = no
    self.name = name
    self.career = career
    self.impossible_time = impossible_time


  def is_applicated(self, box_name):
    return (box_name not in self.impossible_time)

class Shift(object):
  # コマの定義
  SHIFT_BOXES = [
    'day1_1', 'day1_2', 'day1_3',
    'day2_1', 'day2_2', 'day2_3',
    'day3_1', 'day3_2', 'day3_3']
  
  # 各コマの想定人数
  NEED_PEOPLE = [
    1,1,1,
    1,1,1,
    1,1,1]

  def __init__(self, list):
    if list == None:
      self.make_sample()
    else:
      self.list = list
    self.organizations = []

  # ランダムなデータを生成
  def make_sample(self):
    sample_list = []
    for num in range(81):
      sample_list.append(random.randint(0, 1))
    self.list = tuple(sample_list)

  # タプルを1ユーザ単位に分割
  def slice(self):
    sliced = []
    start = 0
    for num in range(9):
      sliced.append(self.list[start:(start + 9)])
      start = start + 9
    return tuple(sliced)
  
  def print_csv(self):
    for line in self.slice():
      print(','.join(map(str, line)))

  # TSV形式でアサイン結果の出力をする
  def print_tsv(self):
    for line in self.slice():
      print("\t".join(map(str, line)))


  # ユーザ番号を指定してコマ名を取得する
  def get_boxes_by_user(self, user_no):
    line = self.slice()[user_no]
    return self.line_to_box(line)

  # 1ユーザ分のタプルからコマ名を取得する
  def line_to_box(self, line):
    result = []
    index = 0
    for e in line:
      if e == 1:
        result.append(self.SHIFT_BOXES[index])
      index = index + 1
    return result

  # コマ番号を指定してアサインされているユーザ番号リストを取得する
  def get_user_nos_by_box_index(self, box_index):
    user_nos = []
    index = 0
    for line in self.slice():
      if line[box_index] == 1:
        user_nos.append(index)
      index += 1
    return user_nos

  # コマ名を指定してアサインされているユーザ番号リストを取得する
  def get_user_nos_by_box_name(self, box_name):
    box_index = self.SHIFT_BOXES.index(box_name)
    return self.get_user_nos_by_box_index(box_index)

  # 想定人数と実際の人数の差分を取得する
  def abs_people_between_need_and_actual(self):
    result = []
    index = 0
    for need in self.NEED_PEOPLE:
      actual = len(self.get_user_nos_by_box_index(index))
      result.append(abs(need - actual))
      index += 1
    return result
  
  # 参加不可能時間に出演することになっているバンド数を取得
  def not_applicated_assign(self):
    count = 0
    for box_name in self.SHIFT_BOXES:
      user_nos = self.get_user_nos_by_box_name(box_name)
      for user_no in user_nos:
        e = self.organizations[user_no]
        if not e.is_applicated(box_name):
          count += 1
    return count

  # 1団体につき1つにアサイン
  def only_one_organization_assign(self):
    count = 0
    index = 0
    for box_name in self.SHIFT_BOXES:
      if sum(self.slice()[index]) == 1:
        count += 1
      index += 1
    return count

  # 経験のある団体を後半に持ってくる
  def applicated_order_count(self):
    shift_box_sum = 0
    count = 0
    for box_name in self.SHIFT_BOXES:
      user_nos = self.get_user_nos_by_box_name(box_name)
      box_order = int(box_name.split('_')[1])
      for user_no in user_nos:
        career = self.organizations[user_no].career
        if box_order > career:
          shift_box_sum += box_order
        else:
          shift_box_sum += career
        count += abs(career - box_order)
    return (count / shift_box_sum)



# 団体定義

# 朝だけ
e0 = Organization(0, "山田", 10, [
    'day1_1'])

# 月・水・金
e1 = Organization(1, "鈴木", 11, [
    'day1_2'
    ])

# 週末だけ
e2 = Organization(2, "佐藤", 12, [
    'day2_1'])

# どこでもOK
e3 = Organization(3, "田中", 2, [
    'day1_3'])

# 夜だけ
e4 = Organization(4, "山口", 1,['day2_2'])

# 平日のみ
e5 = Organization(5, "加藤", 3,['day2_3'])

# 金土日
e6 = Organization(6, "川口", 4,['day3_1'])

# 昼のみ
e7 = Organization(7, "野口", 2, ['day3_2'])

organizations = [e0, e1, e2, e3, e4, e5, e6, e7, e8]

creator.create("FitnessPeopleCount", base.Fitness, weights=(-100.0, -100.0, -100.0, -10.0))
creator.create("Individual", list, fitness=creator.FitnessPeopleCount)

toolbox = base.Toolbox()

toolbox.register("map", futures.map)

toolbox.register("attr_bool", random.randint, 0, 1)
toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, 81)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def evalShift(individual):
  s = Shift(individual)
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

toolbox.register("evaluate", evalShift)
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
    s = Shift(best_ind)
    s.print_csv()
    s.print_tsv()