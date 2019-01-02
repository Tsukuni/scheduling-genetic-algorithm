class Event(object):
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
