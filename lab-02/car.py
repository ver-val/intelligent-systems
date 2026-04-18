class Car:
    def __init__(self, brand, model, year, mileage=0):
        self.brand = brand
        self.model = model
        self.year = year
        self.mileage = mileage

    def drive(self, distance):
        self.mileage += distance

    def describe(self):
        return f"{self.year} {self.brand} {self.model}, mileage: {self.mileage} km"
