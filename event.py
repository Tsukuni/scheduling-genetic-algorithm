import random

class Event(object):
  def __init__(self, list, event_boxes, need_people, input_path, organization_info):
    if list == None:
      self.make_sample()
    else:
      self.list = list
    self.organizations = []
    self.event_boxes = event_boxes
    self.need_people = need_people
    self.input_path = input_path
    self.organization_info = organization_info

  # ランダムなデータを生成
  def make_sample(self):
    sample_list = []
    for num in range(len(self.event_boxes)):
      sample_list.append(random.randint(0, 1))
    self.list = tuple(sample_list)

  # タプルを1ユーザ単位に分割
  def slice(self):
    sliced = []
    start = 0
    event_len = len(self.event_boxes)
    for num in range(event_len):
      sliced.append(self.list[start:(start + event_len)])
      start = start + event_len
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
        result.append(self.event_boxes[index])
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
    box_index = self.event_boxes.index(box_name)
    return self.get_user_nos_by_box_index(box_index)

  # 想定人数と実際の人数の差分を取得する
  def abs_people_between_need_and_actual(self):
    result = []
    index = 0
    for need in self.need_people:
      actual = len(self.get_user_nos_by_box_index(index))
      result.append(abs(need - actual))
      index += 1
    return result
  
  # 参加不可能時間に出演することになっているバンド数を取得
  def not_applicated_assign(self):
    count = 0
    for box_name in self.event_boxes:
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
    for box_name in self.event_boxes:
      if sum(self.slice()[index]) == 1:
        count += 1
      index += 1
    return count

  # 経験のある団体を後半に持ってくる
  def applicated_order_count(self):
    shift_box_sum = 0
    count = 0
    for box_name in self.event_boxes:
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

  # 結果出力
  def out_put_result(self, value, time, no):
    f = open('output3-'+ str(no) + '/' + self.input_path, 'w')
    f.write(str(value)+ '\n')
    f.write(str(time)+'秒'+'\n')
    for line in self.slice():
      f.write(str(("\t".join(map(str, line)))))
      f.write('\n')
    f.close()
