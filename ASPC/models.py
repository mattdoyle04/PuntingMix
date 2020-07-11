from django.db import models
from django.utils import timezone

class Parent(models.Model):
    punter = models.CharField(max_length=200)
    bet_date = models.DateField(default=timezone.now)
    bet_year = models.PositiveIntegerField(default=2020)
    bet_week = models.PositiveIntegerField()
    bet_number = models.PositiveIntegerField()
    bet_legs = models.PositiveIntegerField()
    bet_amount = models.FloatField(default=0.0)
    bet_event = models.CharField(max_length=200)
    bet_odds = models.FloatField(default=0.0)
    bet_win = models.BooleanField()
    bet_potential = models.FloatField(default=0.0)
    bet_cashed = models.BooleanField()
    bet_return = models.FloatField(default=0.0)
    
    def pnl(self):
        return round(self.bet_return - self.bet_amount, 2)
    
    def cum_pnl(self):
        punters_query_set = Parent.objects.order_by('bet_date','punter','bet_number')
        punters_list = [punter.id for punter in punters_query_set]
        current = punters_list.index(self.pk)
        pnl_list = []
        cum_pnl_list = []
        for punter in punters_query_set:
            pnl_list.append(punter.pnl())
        for i in range(0, len(pnl_list)):
            cum_pnl_list.append(sum(pnl_list[0:i+1]))
        return cum_pnl_list[current]

    def cum_average(self):
        punters_query_set = Parent.objects.order_by('bet_date','punter','bet_number')
        punters_list = [punter.id for punter in punters_query_set]
        current = punters_list.index(self.pk)
        pnl_list = []
        ave_pnl_list = []
        for punter in punters_query_set:
            pnl_list.append(punter.pnl())
        for i in range(0, len(pnl_list)):
            try:
                ave_pnl_list.append(sum(pnl_list[0:i+1])/i+1)
            except:
                ave_pnl_list.append(0)
        return ave_pnl_list[current]
    
    def is_coward(self):
        return self.bet_odds < 3
    
    class Meta:
        ordering = ['bet_date','punter','bet_number']
    
    def __str__(self):
        return self.punter + " Wk" + str(self.bet_week) + " Bet" + str(self.bet_number)

        
class Multi(models.Model):
    parent = models.ForeignKey(Parent, on_delete=models.CASCADE)
    bet_leg = models.PositiveIntegerField()
    bet_type = models.CharField(max_length=200)
    bet_team = models.CharField(max_length=200)
    bet_opposition = models.CharField(max_length=200)
    bet_home = models.BooleanField()
    bet_odds = models.FloatField()
    bet_win = models.BooleanField()
    
    def __str__(self):
        return self.bet_team


class Punter(models.Model):
    name = models.CharField(max_length=200)
    week = models.PositiveIntegerField()

class Hit(models.Model):
    visits = models.PositiveIntegerField()