def shape(path):
  file = open('input_data/' + path)
  line = file.read().split('\n')
  EVENT_BOXES = line[0].split(',')
  line.pop(0)
  NEED_PEOPLE = [int(i) for i in line[0].split(',')]
  line.pop(0)
  return (EVENT_BOXES, NEED_PEOPLE, line)