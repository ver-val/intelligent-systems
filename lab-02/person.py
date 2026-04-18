class Person:
    def __init__(self, first_name, last_name, age, city):
        self.first_name = first_name
        self.last_name = last_name
        self.age = age
        self.city = city

    def introduce(self):
        return f"{self.first_name} {self.last_name} is {self.age} years old and lives in {self.city}."


class Student(Person):
    def __init__(self, first_name, last_name, age, city, school, graduation_year, gpa):
        super().__init__(first_name, last_name, age, city)
        self.school = school
        self.graduation_year = graduation_year
        self.gpa = gpa

    def describe_student(self):
        return (
            f"{self.first_name} studies at {self.school}, "
            f"graduates in {self.graduation_year}, GPA: {self.gpa}."
        )
