class Organization(object):
  def __init__(self, no, name, career, impossible_time):
    self.no = no
    self.name = name
    self.career = career
    self.impossible_time = impossible_time


  def is_applicated(self, box_name):
    return (box_name not in self.impossible_time)
