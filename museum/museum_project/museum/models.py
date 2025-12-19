from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

class Exhibition(models.Model):
    title = models.CharField('Название', max_length=200)
    description = models.TextField('Описание')
    date_start = models.DateField('Дата начала')
    date_end = models.DateField('Дата окончания')
    price = models.IntegerField(
        'Цена билета',
        validators=[
            MinValueValidator(0, message='Цена не может быть отрицательной'),
            MaxValueValidator(1000000, message='Цена не может превышать 1,000,000 руб.')
        ]
    )
    
    def __str__(self):
        return self.title
    
    def clean(self):
        if self.date_end < self.date_start:
            raise ValidationError({'date_end': 'Дата окончания не может быть раньше даты начала'})

class Hall(models.Model):
    name = models.CharField('Название зала', max_length=100)
    capacity = models.IntegerField(
        'Вместимость',
        validators=[MinValueValidator(1, message='Вместимость должна быть хотя бы 1')]
    )
    has_projector = models.BooleanField('Есть проектор', default=False)
    
    def __str__(self):
        return self.name

class Session(models.Model):
    exhibition = models.ForeignKey(Exhibition, on_delete=models.CASCADE, related_name='sessions')
    hall = models.ForeignKey(Hall, on_delete=models.CASCADE, related_name='sessions')
    datetime = models.DateTimeField('Дата и время сеанса')
    seats_available = models.IntegerField(
        'Свободных мест',
        validators=[MinValueValidator(0, message='Не может быть отрицательное количество мест')]
    )
    
    def __str__(self):
        return f"{self.exhibition.title} - {self.datetime}"
    
    def clean(self):
        if self.hall and self.seats_available > self.hall.capacity:
            raise ValidationError({'seats_available': 'Не может быть больше мест, чем вместимость зала'})
