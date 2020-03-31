from collections import defaultdict
import csv
import string

def load_risyu(filename):
    index = {c: i for i, c in enumerate(string.ascii_uppercase)}
    courses = {}
    roster = defaultdict(dict)
    with open(filename, encoding='cp932') as f:
        reader = csv.reader(f)
        for i, row in enumerate(reader):
            if i == 0 or not row:
                continue
            course_code = row[index['F']]
            course_name = row[index['G']].strip()
            student_id = row[index['S']]
            student_class_no = row[index['T']]
            student_class_no = '%s-%d' % (student_class_no[:4],
                                          int(student_class_no[4:]))
            student_name = row[index['U']].strip().replace('\u3000', ' ')
            courses[course_code] = course_name
            roster[course_code][student_id] = (student_class_no, student_name)
    return courses, roster

def dump():
    courses, roster = load_risyu('risyu.csv')
    for course_code, course_name in courses.items():
        print(f'{course_code}: {course_name}')
        for student_id in roster[course_code]:
            student_class_no, student_name = roster[course_code][student_id]
            print(f'  {student_class_no} {student_name}')


if __name__ == '__main__':
    dump()
