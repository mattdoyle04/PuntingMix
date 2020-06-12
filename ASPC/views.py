from django.shortcuts import get_object_or_404
from django.views.generic.list import ListView
from django.db.models import Avg, Count, Sum
from .models import Parent, Multi, Punter, Hit
from datetime import datetime

class ParentListView(ListView):
    model = Parent
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        num_punters = Punter.objects.count()
        week_num = datetime.today().isocalendar()[1]
        punter_num = week_num % num_punters

        hits = Hit.objects.first()
        hits.visits = hits.visits + 1
        hits.save()

        whos_turn = Punter.objects.filter(week__exact=punter_num)[0].name

        context['whos_turn'] = whos_turn
        context['hits'] = Hit.objects.first().visits
        context['bet_count'] = Parent.objects.count()
        context['bet_count_wins'] = Parent.objects.filter(bet_win__exact=True).count()
        context['bet_count_losses'] = context['bet_count'] - context['bet_count_wins']
        context['bet_win_ratio'] = round((context['bet_count_wins'] / context['bet_count'])*100,2)
        context['bet_count_multi'] =  Multi.objects.count()
        context['bet_count_multi_wins'] = Multi.objects.filter(bet_win__exact=True).count()
        context['bet_count_multi_losses'] = context['bet_count_multi'] - context['bet_count_multi_wins']
        context['bet_win_ratio_multi'] = round((context['bet_count_multi_wins'] / context['bet_count_multi'])*100,2)
        context['bet_return_total'] = Parent.objects.aggregate(bet_return_sum=Sum('bet_return'))['bet_return_sum']
        context['bet_amount_total'] = Parent.objects.aggregate(bet_amount_sum=Sum('bet_amount'))['bet_amount_sum']
        context['bet_cum_pnl'] = context['bet_return_total'] - context['bet_amount_total']
        context['bet_return_average'] = Parent.objects.aggregate(bet_return_average=Avg('bet_return'))['bet_return_average']

        punts = Parent.objects.all()
        punters = []
        for punt in punts:
            if punt.punter not in punters:
                punters.append(punt.punter)

        punting_data = []
        for punter in punters:
            spent = Parent.objects.filter(punter__exact=punter).aggregate(bet_amount_sum=Sum('bet_amount'))['bet_amount_sum']
            returned = Parent.objects.filter(punter__exact=punter).aggregate(bet_return_sum=Sum('bet_return'))['bet_return_sum']
            profit = round(returned - spent,2)
            punting_data.append({'name':punter,'spent':spent,'returned':returned,'profit':profit})
        
        sorted_punting_data = sorted(punting_data, key=lambda k: k['profit'], reverse=True) 
        context['profit_ladder'] = sorted_punting_data[0]

        if sorted_punting_data[-1]['name'] == "Unsanctioned":
            context['loss_ladder'] = sorted_punting_data[-2]
        else:
            context['loss_ladder'] = sorted_punting_data[-1]

        odds_data = {}
        for punter in punters:
            total_spent = Parent.objects.filter(punter__exact=punter).aggregate(bet_amount_sum=Sum('bet_amount'))['bet_amount_sum']
            bet_count = Parent.objects.filter(punter__exact=punter).annotate(bet_amount_count=Count('bet_amount'))
            sum_product = sum([bet.bet_amount * bet.bet_odds for bet in bet_count])
            weighted_ave = sum_product / total_spent
            odds_data[punter] = weighted_ave
        
        sorted_odds = sorted(odds_data.items(), key=lambda x: x[1])
        
        x,y = sorted_odds[0] 
        if x == "Unsanctioned":
            context['odds_ladder'] = sorted_odds[1]
        else:
            context['odds_ladder'] = sorted_odds[0]

        return context 

class MultiListView(ListView):
    
    def get_queryset(self):
        self.parent = get_object_or_404(Parent, id=self.kwargs['pk'])
        return Multi.objects.filter(parent=self.parent)
    
    
class LeaderboardView(ListView):
    model = Parent
    context_object_name = 'bets'
    template_name = 'ASPC/leaderboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        num_visits = self.request.session.get('num_visits', 0)
        self.request.session['num_visits'] = num_visits + 1
        context['num_visits'] = num_visits
        
        punts = Parent.objects.all()
        punters = []
        for punt in punts:
            if punt.punter not in punters:
                punters.append(punt.punter)

        punting_data = []
        for punter in punters:
            spent = Parent.objects.filter(punter__exact=punter).aggregate(bet_amount_sum=Sum('bet_amount'))['bet_amount_sum']
            returned = Parent.objects.filter(punter__exact=punter).aggregate(bet_return_sum=Sum('bet_return'))['bet_return_sum']
            profit = round(returned - spent,2)
            punting_data.append({'name':punter,'spent':spent,'returned':returned,'profit':profit})
        
        sorted_punting_data = sorted(punting_data, key=lambda k: k['profit'], reverse=True) 
        context['profit_ladder'] = sorted_punting_data
            
        odds_data = {}
        for punter in punters:
            total_spent = Parent.objects.filter(punter__exact=punter).aggregate(bet_amount_sum=Sum('bet_amount'))['bet_amount_sum']
            bet_count = Parent.objects.filter(punter__exact=punter).annotate(bet_amount_count=Count('bet_amount'))
            sum_product = sum([bet.bet_amount * bet.bet_odds for bet in bet_count])
            weighted_ave = sum_product / total_spent
            odds_data[punter] = weighted_ave
        
        sorted_odds = sorted(odds_data.items(), key=lambda x: x[1])
        context['odds_ladder'] = sorted_odds

        cashed_data = {}
        for punter in punters:
            cash_out_win = Parent.objects.filter(punter__exact=punter).filter(bet_cashed__exact=True).filter(bet_win__exact=True).aggregate(win_return=Sum('bet_return'))['win_return']
            cash_out_win_potential = Parent.objects.filter(punter__exact=punter).filter(bet_cashed__exact=True).filter(bet_win__exact=True).aggregate(win_return_potential=Sum('bet_potential'))['win_return_potential']
            cash_out_loss = Parent.objects.filter(punter__exact=punter).filter(bet_cashed__exact=True).filter(bet_win__exact=False).aggregate(loss_return=Sum('bet_return'))['loss_return']
            if cash_out_win and cash_out_loss is not None:
                cashed_data[punter] = cash_out_loss - (cash_out_win_potential - cash_out_win)
            elif cash_out_win is not None and cash_out_loss is None:
                cashed_data[punter] = cash_out_win - cash_out_win_potential
            elif cash_out_loss is not None and cash_out_win is None:
                cashed_data[punter] = cash_out_loss
            else:
                cashed_data[punter] = 0

        sorted_cashed = sorted(cashed_data.items(), key=lambda x: x[1],reverse=True)
        context['cashed_data'] = sorted_cashed

        events = Parent.objects.values('bet_event').annotate(Count('bet_event')).order_by('-bet_event__count')
        event_data = {}
        for event in events:
            event_data[event['bet_event']] = event['bet_event__count']

        context['event_data'] = event_data

        teams = Multi.objects.values('bet_team').annotate(Count('bet_team')).order_by('-bet_team__count')
        team_data = {}
        for team in teams:
            team_data[team['bet_team']] = team['bet_team__count']
        
        context['team_data'] = team_data

        team_cost = Multi.objects.values('bet_team').filter(bet_win=False).filter(parent__bet_cashed=False).annotate(Sum('parent__bet_amount')).order_by('-parent__bet_amount__sum')
        team_cost_data = {}
        for team in team_cost:
            team_cost_data[team['bet_team']] = team['parent__bet_amount__sum']
        
        context['team_cost_data'] = team_cost_data
        
        opposition_cost = Multi.objects.values('bet_opposition').filter(bet_win=False).filter(parent__bet_cashed=False).annotate(Sum('parent__bet_amount')).order_by('-parent__bet_amount__sum')
        opposition_cost_data = {}
        for team in opposition_cost:
            opposition_cost_data[team['bet_opposition']] = team['parent__bet_amount__sum']
        
        context['opposition_cost_data'] = opposition_cost_data

        return context
