from django.db import models

class Annonse(models.Model):
    userprofile = models.ForeignKey('user.Profile')
    timeadded = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    slug = models.CharField(max_length=255)
    fylke = models.ForeignKey('core.County')
    image = models.CharField(max_length=2048, null=True)
    text = models.TextField()
    hidden = models.BooleanField()
    hideage = models.BooleanField()

    age = models.IntegerField()
    ismale = models.BooleanField()

    def get_date(self):
        return timeadded.day + '.' + timeadded.month + '.' + timeadded.year

    def get_gender(self):
        if self.ismale == True:
            return 'Mann'
        else:
            return "Kvinne"

    def compute_gender(self):
        actor = self.userprofile.actor()
        if actor == None:
            self.ismale = False
            return

        if actor.sex == 'm':
            self.ismale = True
        else:
            self.ismale = False

    def compute_age(self):
        actor = self.userprofile.actor()
        if actor == None:
            self.age = 1
            self.save()
            return
        born = userprofile.get_actor().birth_date
        now = datetime.now()
        try: # raised when birth date is February 29 and the current year is not a leap year
            birthday = born.replace(year=now.year)
        except ValueError:
            birthday = born.replace(year=now.year, day=born.day-1)
        if birthday > now:
            self.age = now.year - born.year - 1
        else:
            self.age = now.year - born.year