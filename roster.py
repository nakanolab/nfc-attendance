'''Provides a class and functions that handle enrollments and attendance.'''

from collections import Counter
from collections import defaultdict
import csv
import datetime
import logging
import os.path
import string

RISYU_FILE = 'risyu.csv'  # Downloaded from KIT Inside.


class Roster:
    '''Stores info of enrolled students for all courses that one is in charge.

    Attendance records are stored in the following file under log/ directory:
        attendance-COURSE_CODE-YYYY-MM-DD.log

    Attributes:
        courses: Mapping from course code to course name.
        all_students: For each course code, mapping from ID of enrolled student
            to class No., student name, and sequence No.
        course_code: A particular course code that one is taking attendance for.
        students (property): Mapping from student ID to class No., student name,
            and sequence No. of the students who are enrolled in the particular
            course. This becomes valid only after set_course_code() is called.
        present: A set of student IDs who attended the course.
    '''

    def __init__(self):
        self.courses, self.all_students = load_risyu(RISYU_FILE)
        self.present = set()

    def set_course_code(self, course_code):
        '''Sets course code that one is taking attendance for.

        If the log file exists, adds students whose ID card is already scanned.
        '''
        student_ids = replay_log(course_code)
        setup_logging(course_code)
        self.logger = logging.getLogger()
        self.course_code = course_code
        classes = []
        for student_class_no, _, _ in self.students.values():
            classes.append(student_class_no[:student_class_no.index('-')])
        class_count = Counter(classes)
        self.logger.info('========= クラス人数 =========')
        self.logger.info(', '.join(f'{class_} ({count})' for class_, count
                                   in class_count.most_common()))
        # replay log file
        for student_id in student_ids:
            self.present.add(student_id)
            student_class_no, student_name, _ = self.students[student_id]
            self.logger.info('[log replay] added %s %s %s',
                             student_id, student_class_no, student_name)

    @property
    def students(self):  # 該当コースの履修生
        return self.all_students[self.course_code]

    def check_in(self, student_id):
        '''Checks in an enrolled student.

        Returns:
            A tuple of whether it is a new legit check-in and some informative
            message for showing in the GUI.
        '''
        if student_id not in self.students:
            self.logger.warning('unregistered student: %s', student_id)
            return False, f'未登録の学生\n{student_id}'
        elif student_id in self.present:
            student_class_no, student_name, _ = self.students[student_id]
            self.logger.warning('already checked in: %s', student_id)
            return False, f'チェックイン済\n{student_class_no}\n{student_name}'
        else:
            self.present.add(student_id)
            student_class_no, student_name, _ = self.students[student_id]
            self.logger.info('added %s %s %s',
                             student_id, student_class_no, student_name)
            return True, f'{student_class_no}\n{student_name}'

    def report_absent_students(self):
        '''Writes to the log file a list of absent students.'''
        self.logger.info('======== 欠席者リスト ========')
        for student_id in self.students:
            if student_id not in self.present:
                student_class_no, student_name, student_seqno = \
                    self.students[student_id]
                self.logger.info('absent: [%s] %s %s', student_seqno,
                                                       student_class_no,
                                                       student_name)


def load_risyu(filename):
    '''Reads a specifically formatted CSV file of enrollment info of courses.
    '''
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
            student_seqno = row[index['R']].lstrip('0')
            student_id = row[index['S']]
            student_class_no = row[index['T']]
            student_class_no = '%s-%d' % (student_class_no[:4],
                                          int(student_class_no[4:]))
            student_name = row[index['U']].strip().replace('\u3000', ' ')
            courses[course_code] = course_name
            roster[course_code][student_id] = (student_class_no,
                                               student_name,
                                               student_seqno)
    return courses, roster

def get_log_filename(course_code):
    date = datetime.date.today().strftime('%Y-%m-%d')
    return f'log/attendance-{course_code}-{date}.log'

def replay_log(course_code):
    '''Reads today's log file of the course, if exists, and collects attendance
    records.

    Returns:
        A list of student IDs that were already scanned.
    '''
    filename = get_log_filename(course_code)
    student_ids = []
    if os.path.isfile(filename):
        with open(filename) as f:
            for line in f:
                fields = line.split()
                if len(fields) > 5 and fields[4] == 'added':
                    student_ids.append(fields[5])
    return student_ids

def setup_logging(course_code):
    '''Redirects log messages to log file and to stdout.'''
    format_ = '%(asctime)s %(name)-8s %(levelname)-8s %(message)s'
    logging.basicConfig(level=logging.INFO,
                        format=format_, datefmt='%m/%d %H:%M',
                        filename=get_log_filename(course_code), filemode='a')
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter(format_)
    console.setFormatter(formatter)
    logging.getLogger().addHandler(console)
    logging.getLogger('nfc.clf').setLevel(logging.WARNING)  # to silence NFC log

def dump():
    '''Prints what's in the CSV file.'''
    courses, roster = load_risyu(RISYU_FILE)
    for course_code, course_name in courses.items():
        print(f'{course_code}: {course_name}')
        for student_id in roster[course_code]:
            student_class_no, student_name = roster[course_code][student_id]
            print(f'  {student_class_no} {student_name}')


if __name__ == '__main__':
    dump()
