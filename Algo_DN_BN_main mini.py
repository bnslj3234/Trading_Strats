strat_title = " * Delta Neutral * BankNifty CODE "
strategy_name='BN_Delta_Neutral'; strat_id='BN'
inst_base='BANKNIFTY'; inst_name='NIFTY BANK'; strikes=100; lot_size=25
print("#####------------------------------#####")
print("STARTING",strat_title)
print("#####------------------------------#####")

# from kiteconnect import KiteConnect
import requests,json,time,datetime, os
import pandas as pd, numpy as np, math
import pickle, random
# redis, telegram, random
from scipy.stats import norm
# rRr = redis.Redis(host='127.0.0.1', port=6379, db=0)
# from telegram_details import telegram_activated_bots, telegram_msg
from utility_main import *
# from BS import *
# -----------------------

##### Get inputs
expiry_wise_inputs = {1:{'trade_start_time':datetime.time(9, 37, 59),'combined_premium':100,'trade_close_time':datetime.time(14, 58, 59),'pnl_profit':41000,'pnl_loss':-16000,
                         'delta_move_perc':50.0/100, 'call_qty_delta_neutral_perc':100/100, 'put_qty_delta_neutral_perc':50/100, 'roll_strike_perc':2.0/100,
                         'combined_premium_stop_loss_perc':3000/100, 'strike_selection_round_off':100, 'strike_rollover_diff_from_previous':0,
                         'minimum_trade_qty':100, 'maximum_trade_qty':100, 'index_move_global_sq_off_points':2000,
                         'TRAIL_SL':False, 'CONSIDER_YESTERDAY_PREMIUM':False, 'otm_strike_distance':300,'initial_delta':False,'sum_premium_perc_move' : 0.9, 'index_total_move' : 220, 'last_new_trade_time' :datetime.time(15, 0, 0),
                         'each_leg_stoploss' : 20},
                      2:{'trade_start_time':datetime.time(9, 26, 59),'combined_premium':100,'trade_close_time':datetime.time(15, 11, 59),'pnl_profit':52000,'pnl_loss':-31000,
                         'delta_move_perc':50.0/100, 'call_qty_delta_neutral_perc':100/100, 'put_qty_delta_neutral_perc':50/100, 'roll_strike_perc':2.0/100,
                         'combined_premium_stop_loss_perc':3000/100, 'strike_selection_round_off':100, 'strike_rollover_diff_from_previous':0,
                         'minimum_trade_qty':100, 'maximum_trade_qty':100, 'index_move_global_sq_off_points':2000,
                         'TRAIL_SL':False, 'CONSIDER_YESTERDAY_PREMIUM':False, 'otm_strike_distance':100,'initial_delta' : False,'sum_premium_perc_move' : 2.0, 'index_total_move' : 220, 'last_new_trade_time' :datetime.time(15, 0, 0),
                         'each_leg_stoploss' : 20},
                      3:{'trade_start_time':datetime.time(9, 43, 59),'combined_premium':100,'trade_close_time':datetime.time(14, 41, 59),'pnl_profit':48000,'pnl_loss':-28000,
                         'delta_move_perc':50.3/100, 'call_qty_delta_neutral_perc':100/100, 'put_qty_delta_neutral_perc':50/100, 'roll_strike_perc':50.0/100,
                         'combined_premium_stop_loss_perc':3000/100, 'strike_selection_round_off':100, 'strike_rollover_diff_from_previous':50,
                         'minimum_trade_qty':50, 'maximum_trade_qty':50, 'index_move_global_sq_off_points':2000,
                         'TRAIL_SL':False, 'CONSIDER_YESTERDAY_PREMIUM':False, 'otm_strike_distance':0,'initial_delta' : False,'sum_premium_perc_move' : 25, 'index_total_move' : 3000, 'last_new_trade_time' :datetime.time(15, 15, 0),
                         'each_leg_stoploss' : 0.16},
                      4:{'trade_start_time':datetime.time(14, 5, 28),'combined_premium':100,'trade_close_time':datetime.time(15, 13, 0),'pnl_profit':29400,'pnl_loss':-25800,
                         'delta_move_perc':50.3/100, 'call_qty_delta_neutral_perc':100/100, 'put_qty_delta_neutral_perc':50/100, 'roll_strike_perc':50.0/100,
                         'combined_premium_stop_loss_perc':3000/100, 'strike_selection_round_off':100, 'strike_rollover_diff_from_previous':50,
                         'minimum_trade_qty':25, 'maximum_trade_qty':25, 'index_move_global_sq_off_points':2000,
                         'TRAIL_SL':False, 'CONSIDER_YESTERDAY_PREMIUM':False, 'otm_strike_distance':500,'initial_delta' : False,'sum_premium_perc_move' : 25 , 'index_total_move' : 3000, 'last_new_trade_time' :datetime.time(15, 15, 0),
                         'each_leg_stoploss' : 0.03},
                      5:{'trade_start_time':datetime.time(9, 42, 59),'combined_premium':100,'trade_close_time':datetime.time(15, 12, 59),'pnl_profit':30000,'pnl_loss':-22000,
                         'delta_move_perc':50.3/100, 'call_qty_delta_neutral_perc':100/100, 'put_qty_delta_neutral_perc':50/100, 'roll_strike_perc':50.0/100,
                         'combined_premium_stop_loss_perc':3000/100, 'strike_selection_round_off':100, 'strike_rollover_diff_from_previous':50,
                         'minimum_trade_qty':100, 'maximum_trade_qty':100, 'index_move_global_sq_off_points':2000,
                         'TRAIL_SL':False, 'CONSIDER_YESTERDAY_PREMIUM':False, 'otm_strike_distance':0,'initial_delta' : False,'sum_premium_perc_move' : 25, 'index_total_move' : 3000, 'last_new_trade_time' :datetime.time(15, 15, 0),
                         'each_leg_stoploss' : 0.11}}

risk_free_return = rf = 3.6/100
dividend=q=0
days_in_year=365
freak_trade_zone_points=20
freak_trade_tick_wait=2
switch_straddle_wait_secs=30

# Yesterday combine premium
try:
    db_input = open(strat_id+'_Combined_Premium', 'rb')
    yesterday_combined_premium = pickle.load(db_input)
    db_input.close()
except:
    yesterday_combined_premium=1000    
print("Yesterday's Combined Premium -- ",yesterday_combined_premium)
#----------------------------

#last_new_trade_time = datetime.time(15, 15, 0)
market_close_time = datetime.time(15, 29, 0)   # Better NOT to change it
#---------------

while True:
    decision = market_hours(open_time = datetime.time(9, 5, 0))
    if decision=='OPEN':
        print('##### MARKET OPEN :: Sync in Strategy #####')
        break
    get_up_time=datetime.datetime.fromtimestamp(decision+time.time()).strftime('%H:%M:%S %A, %d-%b-%Y')
    print('Login Credentials will be updated again @ ',get_up_time)
    time.sleep(random.sample([1,2,3],1)[0])
    telegram_msg("Scheduling"+strat_title+  "@ "+get_up_time)
    time.sleep(decision)

from telegram_details import telegram_activated_bots, telegram_msg
telegram_msg("Running"+strat_title)
# -----------------------

########### Sync with Zerodha #############
sleep_secs = wake_up_time(wakeup_at = datetime.time(9, 41, 0))
time.sleep(sleep_secs)
login_credentials = pickle.loads(rRr.get('MASTER_login'))
inst = pickle.loads(rRr.get('inst_ALL'))
inst_req = pickle.loads(rRr.get('inst_REQ'))
token_info_req = pickle.loads(rRr.get('token_info_REQ'))
inst_req_index = pickle.loads(rRr.get('inst_'+strat_id))
token_info_req_index = pickle.loads(rRr.get('token_info_'+strat_id))

### Calculate remaining expiry days
index_token = inst[inst.name==inst_name]['instrument_token'].iloc[0]
#---------------------
while True:
    try:
        index_price = login_credentials['kite'].ltp(index_token)[str(index_token)]['last_price']
        break
    except:time.sleep(.5)

ATM_price = round(index_price/strikes)*strikes
expiry_date = [y['expiry'] for x,y in token_info_req_index.items() if y['strike']==ATM_price and y['instrument_type']=='CE'][0]
all_remaining_dates = [datetime.datetime.today().date()]
current_date = datetime.datetime.today().date()
while current_date < expiry_date:
    current_date += datetime.timedelta(days=1)
    all_remaining_dates.append(current_date)
all_remaining_dates = [x for x in all_remaining_dates if x not in nse_calendar and x.strftime("%A") not in ['Saturday','Sunday']]
expiry_days = len(all_remaining_dates)
print("Number of remaining days to Weekly Expiry: ",expiry_days)

def cal_expiry_days():
    current = datetime.datetime.time(datetime.datetime.now())
    if datetime.datetime.now().time() > datetime.time(15, 30, 0): return expiry_days-1
    diff = datetime.datetime.combine(datetime.date.today(), datetime.time(15, 30, 0)) - datetime.datetime.combine(datetime.date.today(), current)
    return expiry_days-1 + (diff.seconds)/22500

### --- All variable ---
delta_move_perc = expiry_wise_inputs[expiry_days]['delta_move_perc']
call_qty_delta_neutral_perc = expiry_wise_inputs[expiry_days]['call_qty_delta_neutral_perc']
put_qty_delta_neutral_perc = expiry_wise_inputs[expiry_days]['put_qty_delta_neutral_perc']
roll_strike_perc = expiry_wise_inputs[expiry_days]['roll_strike_perc']
combined_premium_stop_loss_perc = expiry_wise_inputs[expiry_days]['combined_premium_stop_loss_perc']
strike_selection_round_off = expiry_wise_inputs[expiry_days]['strike_selection_round_off']
strike_rollover_diff_from_previous = expiry_wise_inputs[expiry_days]['strike_rollover_diff_from_previous']
minimum_trade_qty = expiry_wise_inputs[expiry_days]['minimum_trade_qty']
maximum_trade_qty = expiry_wise_inputs[expiry_days]['maximum_trade_qty']
index_move_global_sq_off_points = expiry_wise_inputs[expiry_days]['index_move_global_sq_off_points']
TRAIL_SL = expiry_wise_inputs[expiry_days]['TRAIL_SL']
CONSIDER_YESTERDAY_PREMIUM = expiry_wise_inputs[expiry_days]['CONSIDER_YESTERDAY_PREMIUM']

trade_start_time = expiry_wise_inputs[expiry_days]['trade_start_time']
new_straddle_sell_time = trade_start_time
combined_premium = expiry_wise_inputs[expiry_days]['combined_premium']
if CONSIDER_YESTERDAY_PREMIUM:combined_premium=min(yesterday_combined_premium,combined_premium)
trade_close_time = expiry_wise_inputs[expiry_days]['trade_close_time']
profit_realize = expiry_wise_inputs[expiry_days]['pnl_profit']
loss_realize = expiry_wise_inputs[expiry_days]['pnl_loss']
minimum_trade_qty_fix=minimum_trade_qty
### Jatin Changes ###
otm_strike_distance = expiry_wise_inputs[expiry_days]['otm_strike_distance']
initial_delta = expiry_wise_inputs[expiry_days]['initial_delta']
sum_premium_perc_move = expiry_wise_inputs[expiry_days]['sum_premium_perc_move']
index_total_move = expiry_wise_inputs[expiry_days]['index_total_move']
each_leg_stoploss = expiry_wise_inputs[expiry_days]['each_leg_stoploss']
last_new_trade_time = expiry_wise_inputs[expiry_days]['last_new_trade_time']


### Fut & Options
def get_req_straddle_option_pair(fut_price, previous_future_price, previous_strike, strike_rollover_diff_from_previous):
    req_strike = round(fut_price/strike_selection_round_off)*strike_selection_round_off
    if strike_rollover_diff_from_previous==0 or previous_strike=='' or previous_future_price=='':
        req_strike=req_strike
    elif fut_price<previous_future_price:
        req_strike = min(req_strike, previous_strike-strike_rollover_diff_from_previous)
    elif fut_price>previous_future_price:
        req_strike = max(req_strike, previous_strike+strike_rollover_diff_from_previous)
    req_strike = round(req_strike/strike_selection_round_off)*strike_selection_round_off
    ### Jatin Changes ###
    call_req_strike = req_strike + otm_strike_distance
    put_req_strike = req_strike - otm_strike_distance
    call_opt_token = [x for x,y in token_info_req_index.items() if y['strike']==call_req_strike and y['instrument_type']=='CE'][0]
    put_opt_token = [x for x,y in token_info_req_index.items() if y['strike']==put_req_strike and y['instrument_type']=='PE'][0]
    return call_opt_token, put_opt_token # Call Token, Put Token
   
def spot_to_weekly_fut(spot_price):
    days = cal_expiry_days()
    return spot_price*math.exp(rf*days/days_in_year)

def cal_call_put_straddle_qty(call_D, put_D, call_qty, put_qty,initial_delta):
    if initial_delta == True:
        call_D=abs(call_D); put_D=abs(put_D)
        previous_call_qty=call_qty; previous_put_qty=put_qty
        if put_D<call_D:
            if call_qty==0:call_qty=minimum_trade_qty
            put_qty = round((call_D*call_qty/put_D)/lot_size)*lot_size
            if put_qty<=maximum_trade_qty and put_qty>=previous_put_qty: return call_qty, put_qty
            if put_qty>maximum_trade_qty:
                call_qty=round((put_D*maximum_trade_qty/call_D)/lot_size)*lot_size
                return call_qty, maximum_trade_qty
            if put_qty<previous_put_qty:
                call_qty=round((put_D*previous_put_qty/call_D)/lot_size)*lot_size
                return call_qty, previous_put_qty
        if put_D>call_D:
            if put_qty==0:put_qty=minimum_trade_qty
            call_qty = round((put_D*put_qty/call_D)/lot_size)*lot_size
            if call_qty<=maximum_trade_qty and call_qty>=previous_call_qty: return call_qty, put_qty
            if call_qty>maximum_trade_qty:
                put_qty=round((call_D*maximum_trade_qty/put_D)/lot_size)*lot_size
                return maximum_trade_qty, put_qty
            if call_qty<previous_call_qty:
                put_qty=round((call_D*previous_call_qty/put_D)/lot_size)*lot_size
                return previous_call_qty, put_qty
    elif initial_delta == False:
        call_qty=minimum_trade_qty
        put_qty=minimum_trade_qty
        return call_qty,put_qty

def change_qty_trade(new_qty,old_qty):
    if new_qty==old_qty:return 'BUY',0
    if new_qty>old_qty:return 'SELL',new_qty-old_qty
    if new_qty<old_qty:return 'BUY',old_qty-new_qty

def save_combined_premium():
    index_price = login_credentials['kite'].ltp(index_token)[str(index_token)]['last_price']
    fut_price=spot_to_weekly_fut(index_price)
    req_strike = round(fut_price/strike_selection_round_off)*strike_selection_round_off
    token_info_req_index = pickle.loads(rRr.get('token_info_'+strat_id))
    if math.floor(cal_expiry_days())==0:
        nearest_weekly_expiry=list(set(inst[(inst.name=='NIFTY')]['expiry'].tolist()))
        nearest_weekly_expiry.sort();    nearest_weekly_expiry=nearest_weekly_expiry[1]
        inst_req = inst[((inst.name==inst_base)&(inst.segment=='NFO-OPT')&(inst.expiry==nearest_weekly_expiry))]
        token_info_req_index = {x['instrument_token']:x for x in inst_req.to_dict('records')}
    call_opt_token = [x for x,y in token_info_req_index.items() if y['strike']==req_strike and y['instrument_type']=='CE'][0]
    put_opt_token = [x for x,y in token_info_req_index.items() if y['strike']==req_strike and y['instrument_type']=='PE'][0]
    all_price = login_credentials['kite'].ltp([call_opt_token,put_opt_token])
    combined_price = sum([y['last_price'] for x,y in all_price.items()])
    db_input = open(strat_id+'_Combined_Premium', 'wb')
    pickle.dump(combined_price, db_input)
    db_input.close()
    print("Saved combined Premium")
#---------------------

def save_data(row): #['Time','Spot','Future','Call Strike','Put Strike','Call IV','Put IV','Call Delta','Put Delta','Call LTP','Put LTP','Call Qty','Put Qty','Combined SL','PnL']
    try:
        data_path = os.getcwd()+'\\saved data\\'
        data_date = str(datetime.datetime.now().date()).replace('-','_')
        data_fn = data_date+'_'+strategy_name+'.csv'
        col_head=['Time','Spot','Future','Call Strike','Put Strike','Call IV','Put IV','Call Delta','Put Delta','Call LTP','Put LTP','Call Qty','Put Qty','Combined SL','PnL']
        if data_fn not in os.listdir(data_path):  
            fo=open(data_path+data_fn,'a+')
            fo.write(','.join([str(x) for x in col_head]))
            fo.write('\n'); fo.close()
        fo=open(data_path+data_fn,'a+')
        fo.write(','.join([str(x) for x in row]))
        fo.write('\n'); fo.close()
    except Exception as e:
        print("Error writing data for ",time_now(),str(e))
# -----------------------

TRADE = True
straddle_pos=0; FIRST_straddle=True; 
push_orders =0; check_move = True ;start_threshold = 0.3; morning_sum_time = datetime.time(9, 55, 00)
previous_strike=''; previous_future_price=''
call_qty=0; put_qty=0
all_trades=[]; current_pnl=0; all_prices={}
call_option_price=0; put_option_price=0

sleep_secs = wake_up_time(wakeup_at = trade_start_time)
time.sleep(sleep_secs)

exit_time_input = (datetime.datetime.combine(datetime.date.today(), trade_start_time) + datetime.timedelta(seconds=5)).time()
rRr.set('EXIT_'+strategy_name,'0')
EXIT_ALL=0

pnl_check_time = (datetime.datetime.combine(datetime.date.today(), trade_start_time) + datetime.timedelta(seconds=5)).time()
all_ac_info=pickle.loads(rRr.get('all_ac_info'))
pnl_ac = [y for x,y in all_ac_info.items() if y[strategy_name]]
if len(pnl_ac)>0:
    req_user=pnl_ac[0]['USER_ID'];    req_pnl_factor=pnl_ac[0]['Qty Multiple']
else:
    pnl_ac = [y for x,y in all_ac_info.items() if y['Type']=='Master']
    req_user=pnl_ac[0]['USER_ID'];    req_pnl_factor=pnl_ac[0]['Qty Multiple']
if req_pnl_factor==0:req_pnl_factor=1

pubsub = rRr.pubsub()
pubsub.subscribe(['ZERODHA_TICKS_UPDATE'])
print("Reading market, waiting for Signals.....",'\n')

for item in pubsub.listen():
    if datetime.datetime.today().time() > market_close_time:
        save_combined_premium()
        pubsub.unsubscribe()
        break
    if item['channel'].decode() == 'ZERODHA_TICKS_UPDATE' and TRADE:
        try:
            data = pickle.loads(item['data'])
            for d in data:all_prices[d['instrument_token']] = d['last_price']
        except:continue
        
        try:index_price = [x['last_price'] for x in data if x['instrument_token']==index_token][0]
        except:continue
        
        fut_price = spot_to_weekly_fut(index_price)
        print("Index Price is %s :: Futures is %s :: Strategy P&L is %s"%(str(round(index_price,0)),str(round(fut_price,0)),str(round(current_pnl,0))),sep='',end="\r",flush=True)

        # ---------- Check Straddle
        if straddle_pos==0 and push_orders == 0 and morning_sum_time <= datetime.datetime.today().time():
            
            call_option_token, put_option_token = get_req_straddle_option_pair(fut_price, previous_future_price, previous_strike, strike_rollover_diff_from_previous)
            
            call_sell_trading_symbol = token_info_req_index[call_option_token]['tradingsymbol']
            put_sell_trading_symbol = token_info_req_index[put_option_token]['tradingsymbol']

            call_strike = int(token_info_req_index[call_option_token]['strike'])
            put_strike = int(token_info_req_index[put_option_token]['strike'])

            try:call_option_price = [x['last_price'] for x in data if x['instrument_token']==call_option_token][0]
            except:pass
            try:put_option_price = [x['last_price'] for x in data if x['instrument_token']==put_option_token][0]
            except:pass
            if call_option_price==0 or put_option_price==0: continue
            
            if check_move == True:
                to_check_combined_premium = call_option_price+put_option_price
                try:index_price_s = [x['last_price'] for x in data if x['instrument_token']==index_token][0]
                except:continue
                
                check_move = False
                
            if((index_price >index_price_s + to_check_combined_premium*(1+start_threshold)) & (index_price <index_price_s - to_check_combined_premium*(1+start_threshold))):
                ATM_price = round(index_price/strikes)*strikes
                push_orders=1
                call_option_token, put_option_token = get_req_straddle_option_pair(fut_price, previous_future_price, previous_strike, strike_rollover_diff_from_previous)
                call_sell_trading_symbol = token_info_req_index[call_option_token]['tradingsymbol']
                put_sell_trading_symbol = token_info_req_index[put_option_token]['tradingsymbol']

                call_strike = int(token_info_req_index[call_option_token]['strike'])
                put_strike = int(token_info_req_index[put_option_token]['strike'])
                try:call_option_price = [x['last_price'] for x in data if x['instrument_token']==call_option_token][0]
                except:pass
                try:put_option_price = [x['last_price'] for x in data if x['instrument_token']==put_option_token][0]
                except:pass
                if call_option_price==0 or put_option_price==0: continue
            
        #-------------Sell straddle
        if push_orders == 1 and straddle_pos==0 and trade_start_time<datetime.datetime.today().time()<last_new_trade_time and new_straddle_sell_time<datetime.datetime.today().time():
            call_option_token, put_option_token = get_req_straddle_option_pair(fut_price, previous_future_price, previous_strike, strike_rollover_diff_from_previous)
            
            call_sell_trading_symbol = token_info_req_index[call_option_token]['tradingsymbol']
            put_sell_trading_symbol = token_info_req_index[put_option_token]['tradingsymbol']

            call_strike = int(token_info_req_index[call_option_token]['strike'])
            put_strike = int(token_info_req_index[put_option_token]['strike'])

            try:call_option_price = [x['last_price'] for x in data if x['instrument_token']==call_option_token][0]
            except:pass
            try:put_option_price = [x['last_price'] for x in data if x['instrument_token']==put_option_token][0]
            except:pass
            if call_option_price==0 or put_option_price==0: continue

            if FIRST_straddle:
                if call_option_price+put_option_price < combined_premium:
                    print("Futures is %s :: Combined Premium %d is less than required trade premium %d"%(str(round(fut_price,0)),call_option_price+put_option_price, combined_premium),sep='',end="\r",flush=True)
                    continue
                morning_combined_premium = call_option_price+put_option_price
                morning_call_sell_option_price = call_option_price
                morning_put_sell_option_price = put_option_price
                combined_premium_new_sl = morning_combined_premium*(1+combined_premium_stop_loss_perc)
                if CONSIDER_YESTERDAY_PREMIUM:combined_premium_new_sl = min(yesterday_combined_premium,combined_premium_new_sl)
                combined_premium_initial_sl = combined_premium_new_sl
                morning_future_price = fut_price
                NO_FREAK_TRADE=True; freak_tick_list=[]
                FIRST_straddle=False

            nextstrike_call_sell_option_price = call_option_price
            nextstrike_put_sell_option_price = put_option_price
            nextstrike_combined_premium = nextstrike_call_sell_option_price + nextstrike_put_sell_option_price
            call_IV = BS_call_vol(index_price, call_strike, rf, cal_expiry_days()/days_in_year, call_option_price, q)
            put_IV = BS_put_vol(index_price, put_strike, rf, cal_expiry_days()/days_in_year, put_option_price, q)

            call_D = BS_DeltaC(index_price, call_strike, rf, cal_expiry_days()/days_in_year, q, call_IV)
            put_D = BS_DeltaP(index_price, put_strike, rf, cal_expiry_days()/days_in_year, q, put_IV)
            if np.isnan(call_IV) or np.isnan(put_IV) or np.isnan(call_D) or np.isnan(put_D):
                print(time_now(),' :: Call Put IV & Delta Issue :: ',call_IV,put_IV,call_D,put_D)
                continue

            call_qty, put_qty = cal_call_put_straddle_qty(call_D, put_D, call_qty, put_qty,initial_delta)
            
            signal_list=[["SELL",call_sell_trading_symbol,'NFO','MIS','TRADE_NEW',call_qty],
                         ["SELL",put_sell_trading_symbol,'NFO','MIS','TRADE_NEW',put_qty]]
            
            notification_msg = strategy_name +  " :: Selling Straddle %s (Qty. %d) & %s (Qty. %d)"%(call_sell_trading_symbol, call_qty, put_sell_trading_symbol, put_qty)
            print(notification_msg,' :: ', time_now())
            signal_info = {"ALGO":strategy_name, "telegram_msg":notification_msg, "SIGNALS":signal_list }
            rRr.publish('ORDER_MGMT_SYS', json.dumps(signal_info))

            delta_move_lower_price=fut_price*(1-delta_move_perc);    delta_move_upper_price=fut_price*(1+delta_move_perc)
            strike_move_lower_price=fut_price*(1-roll_strike_perc);    strike_move_upper_price=fut_price*(1+roll_strike_perc)
            # new range for wednesday and thursday
            strike_move_lower_price = max(strike_move_lower_price, fut_price - min((nextstrike_combined_premium)* sum_premium_perc_move, index_total_move))
            strike_move_upper_price = min(strike_move_upper_price, fut_price + min((nextstrike_combined_premium)* sum_premium_perc_move, index_total_move))
            
            #strike_move_lower_price = 
            print("Combined Premium for Call %d and Put %d is %d"%(call_option_price,put_option_price,call_option_price+put_option_price))
            print("SL on Combined Premium is ",combined_premium_new_sl)
            print("-"*30,"\nLower range for Delta neutral is %d :: Index is %s :: Upper range for Delta neutral is %d"%(delta_move_lower_price,fut_price,delta_move_upper_price))
            print("Lower range for Strike Change is %d :: Index is %s :: Upper range for Strike Change is %d"%(strike_move_lower_price,fut_price,strike_move_upper_price),'\n','-'*60)
            straddle_pos=-1; print('-'*30); previous_future_price = fut_price
            all_trades.extend([[call_option_token,call_sell_trading_symbol,"SELL",call_qty,call_option_price],
                                [put_option_token,put_sell_trading_symbol,"SELL",put_qty,put_option_price]])

        #---------- individual leg square-off
        try:live_call_option_price = [x['last_price'] for x in data if x['instrument_token']==call_option_token][0]
        except:pass
        try:live_put_option_price = [x['last_price'] for x in data if x['instrument_token']==put_option_token][0]
        except:pass
        if live_call_option_price==0 or live_put_option_price==0: continue
            
        if push_orders == 1 and live_call_option_price >= (1+each_leg_stoploss)*morning_call_sell_option_price and call_qty>0 :
            signal_list=[["BUY",call_sell_trading_symbol,'NFO','MIS','TRADE_NEW',call_qty],
                         ["BUY",put_sell_trading_symbol,'NFO','MIS','TRADE_NEW',0]]
            notification_msg = strategy_name +  " :: Squaring off Stop Loss Hit Call leg %s (All Qty. %d) triggered at Price : %d Remaining Put Qty : %d"%(call_sell_trading_symbol, call_qty,live_call_option_price, put_qty)
            print(notification_msg,' :: ', time_now())
            signal_info = {"ALGO":strategy_name, "telegram_msg":notification_msg, "SIGNALS":signal_list }
            rRr.publish('ORDER_MGMT_SYS', json.dumps(signal_info))
            call_qty = 0
                
        
        if push_orders == 1 and live_put_option_price >= (1+each_leg_stoploss)*morning_put_sell_option_price and put_qty>0 :
            signal_list=[["BUY",call_sell_trading_symbol,'NFO','MIS','TRADE_NEW',0],
                         ["BUY",put_sell_trading_symbol,'NFO','MIS','TRADE_NEW',put_qty]]
                
            notification_msg = strategy_name +  " :: Squaring off Stop Loss Hit Put leg %s (All Qty. %d) triggered at Price : %d Remaining Call Qty : %d"%(put_sell_trading_symbol, put_qty,live_put_option_price,call_qty)
            print(notification_msg,' :: ', time_now())
            signal_info = {"ALGO":strategy_name, "telegram_msg":notification_msg, "SIGNALS":signal_list }
            rRr.publish('ORDER_MGMT_SYS', json.dumps(signal_info))
            put_qty = 0

        
        # ---------- Delta
        if push_orders == 1 and straddle_pos!=0:
            try:call_option_price = [x['last_price'] for x in data if x['instrument_token']==call_option_token][0]
            except:pass
            try:put_option_price = [x['last_price'] for x in data if x['instrument_token']==put_option_token][0]
            except:pass
            if call_option_price==0 or put_option_price==0: continue

            call_IV = BS_call_vol(index_price, call_strike, rf, cal_expiry_days()/days_in_year, call_option_price, q)
            put_IV = BS_put_vol(index_price, put_strike, rf, cal_expiry_days()/days_in_year, put_option_price, q)

            call_D = BS_DeltaC(index_price, call_strike, rf, cal_expiry_days()/days_in_year, q, call_IV)
            put_D = BS_DeltaP(index_price, put_strike, rf, cal_expiry_days()/days_in_year, q, put_IV)
            if np.isnan(call_IV) or np.isnan(put_IV) or np.isnan(call_D) or np.isnan(put_D):
                print(time_now(),' :: Call Put IV & Delta Issue :: ',call_IV,put_IV,call_D,put_D)
                continue
        
        #---------- Strike change square-off
        if push_orders == 1 and straddle_pos!=0 and (fut_price<=strike_move_lower_price or fut_price>=strike_move_upper_price) and trade_start_time<datetime.datetime.today().time()<last_new_trade_time:

            signal_list=[["BUY",call_sell_trading_symbol,'NFO','MIS','TRADE_NEW',call_qty],
                         ["BUY",put_sell_trading_symbol,'NFO','MIS','TRADE_NEW',put_qty]]
            notification_msg = strategy_name +  " :: Squaring off Straddle %s (All Qty. %d) & %s (All Qty. %d)"%(call_sell_trading_symbol, call_qty, put_sell_trading_symbol, put_qty)
            print(notification_msg,' :: ', time_now())
            signal_info = {"ALGO":strategy_name, "telegram_msg":notification_msg, "SIGNALS":signal_list }
            rRr.publish('ORDER_MGMT_SYS', json.dumps(signal_info))
            straddle_pos=0; print('-'*30); previous_strike=call_strike
            minimum_trade_qty = max(minimum_trade_qty_fix, min(call_qty,put_qty))
            all_trades.extend([[call_option_token,call_sell_trading_symbol,"BUY",call_qty,call_option_price],
                                [put_option_token,put_sell_trading_symbol,"BUY",put_qty,put_option_price]])
            new_straddle_sell_time = (datetime.datetime.combine(datetime.date.today(), datetime.datetime.today().time()) + datetime.timedelta(seconds=switch_straddle_wait_secs)).time()

        #---------- Manage Delta neutral
        if push_orders == 1 and straddle_pos!=0 and (fut_price<=delta_move_lower_price or fut_price>=delta_move_upper_price) and trade_start_time<datetime.datetime.today().time()<last_new_trade_time:

            new_call_qty, new_put_qty = cal_call_put_straddle_qty(call_D, put_D, call_qty, put_qty,initial_delta)
            call_incr_qty = round(change_qty_trade(new_call_qty,call_qty)[1]*call_qty_delta_neutral_perc/lot_size)*lot_size
            put_incr_qty = round(change_qty_trade(new_put_qty,put_qty)[1]*put_qty_delta_neutral_perc/lot_size)*lot_size
            call_delta_signal=change_qty_trade(new_call_qty,call_qty)[0]; put_delta_signal=change_qty_trade(new_put_qty,put_qty)[0]
            signal_list=[[call_delta_signal,call_sell_trading_symbol,'NFO','MIS','TRADE_NEW',call_incr_qty],
                         [put_delta_signal,put_sell_trading_symbol,'NFO','MIS','TRADE_NEW',put_incr_qty]]
            if call_delta_signal=='BUY':call_qty-=call_incr_qty
            elif call_delta_signal=='SELL':call_qty+=call_incr_qty
            if put_delta_signal=='BUY':put_qty-=put_incr_qty
            elif put_delta_signal=='SELL':put_qty+=put_incr_qty
            notification_msg = strategy_name +  " :: Managing Straddle %s (New Qty. %d) & %s (New Qty. %d)"%(call_sell_trading_symbol, call_qty, put_sell_trading_symbol, put_qty)
            print(notification_msg,' :: ', time_now())
            signal_info = {"ALGO":strategy_name, "telegram_msg":notification_msg, "SIGNALS":signal_list }
            rRr.publish('ORDER_MGMT_SYS', json.dumps(signal_info))
            delta_move_lower_price=fut_price*(1-delta_move_perc);    delta_move_upper_price=fut_price*(1+delta_move_perc)
            print("-"*30,"\nLower range for Delta neutral is %d :: Index is %s :: Upper range for Delta neutral is %d"%(delta_move_lower_price,fut_price,delta_move_upper_price),'\n','-'*60)
            all_trades.extend([[call_option_token,call_sell_trading_symbol,call_delta_signal,call_incr_qty,call_option_price],
                               [put_option_token,put_sell_trading_symbol,put_delta_signal,put_incr_qty,put_option_price]])

        #---------- Trail Stop loss
        if push_orders == 1 and TRAIL_SL and straddle_pos!=0 and morning_combined_premium>(call_option_price+put_option_price) and morning_combined_premium<combined_premium_new_sl:
            if combined_premium_new_sl > combined_premium_initial_sl-(morning_combined_premium-(call_option_price+put_option_price)):
                #print("Current combined SL price is ", combined_premium_new_sl)
                combined_premium_new_sl = max(morning_combined_premium, combined_premium_initial_sl-(morning_combined_premium-(call_option_price+put_option_price)))
                print("Updating combined SL price to ", combined_premium_new_sl,' @ ',time_now())
                print("----------------------------------------------")

        #---- User manual exit
        if push_orders == 1 and datetime.datetime.today().time()>exit_time_input:
            EXIT_ALL = json.loads(rRr.get('EXIT_'+strategy_name))
            exit_time_input = (datetime.datetime.combine(datetime.date.today(), exit_time_input) + datetime.timedelta(seconds=5)).time()
            if EXIT_ALL==1:print("--- Manual Exit input received ---")

        #---- Check P&L
        if push_orders == 1 and datetime.datetime.today().time()>pnl_check_time:
            PnL = pickle.loads(rRr.get('PnL'))
            try:current_pnl = PnL[req_user][strategy_name]/req_pnl_factor
            except Exception as pnl_err:
                print("P&L Error :: ",pnl_err)
            pnl_check_time = (datetime.datetime.combine(datetime.date.today(), pnl_check_time) + datetime.timedelta(seconds=3)).time()        

        #---------- Freak Trade
        if push_orders == 1 and straddle_pos!=0 and combined_premium_new_sl>(call_option_price+put_option_price):
            freak_tick_list=[]
        if push_orders == 1 and straddle_pos!=0 and combined_premium_new_sl<(call_option_price+put_option_price):
            if len(freak_tick_list)>freak_trade_tick_wait:NO_FREAK_TRADE=True
            if (call_option_price+put_option_price)>combined_premium_new_sl+freak_trade_zone_points:
                freak_tick_list.append(call_option_price+put_option_price)
                NO_FREAK_TRADE=False
                if len(freak_tick_list)>freak_trade_tick_wait:NO_FREAK_TRADE=True
        
        #---------- Complete Square-off -- SL / Manual / Exit time
        if push_orders == 1 and straddle_pos!=0:
            INDEX_MOVE_SQOFF = abs(morning_future_price - fut_price)>=index_move_global_sq_off_points
            PnL_SQOFF = current_pnl>=profit_realize or current_pnl<=loss_realize
            SL_SQOFF = current_pnl<0 and combined_premium_new_sl<(call_option_price+put_option_price) and NO_FREAK_TRADE
        if push_orders == 1 and straddle_pos!=0 and (INDEX_MOVE_SQOFF or PnL_SQOFF or SL_SQOFF or datetime.datetime.today().time()>trade_close_time or EXIT_ALL==1):
            print('INDEX_MOVE_SQOFF:',INDEX_MOVE_SQOFF); print('PnL_SQOFF:',PnL_SQOFF); print('SL_SQOFF:',SL_SQOFF)
            signal_list=[["BUY",call_sell_trading_symbol,'NFO','MIS','TRADE_NEW',call_qty],
                         ["BUY",put_sell_trading_symbol,'NFO','MIS','TRADE_NEW',put_qty]]
            notification_msg = strategy_name +  " :: Squaring off Straddle %s (All Qty. %d) & %s (All Qty. %d)"%(call_sell_trading_symbol, call_qty, put_sell_trading_symbol, put_qty)
            print(notification_msg,' :: ', time_now())
            signal_info = {"ALGO":strategy_name, "telegram_msg":notification_msg, "SIGNALS":signal_list }
            rRr.publish('ORDER_MGMT_SYS', json.dumps(signal_info))
            straddle_pos=0; print('-'*30); TRADE=False            
            
        #---------- Write data
        try:
            save_data([time_now(), index_price, fut_price, call_strike, put_strike, call_IV, put_IV, call_D, put_D,
                                call_option_price, put_option_price, call_qty, put_qty,combined_premium_new_sl,current_pnl])
        except Exception as sd:
            print("SAVE DATA :: ",str(sd))
print("#####------------------------------#####")
print("CLOSING CODE")
print("#####------------------------------#####")
telegram_msg("Closing"+strat_title)

sleep_secs = wake_up_time(wakeup_at = datetime.time(8,45,0))
time.sleep(sleep_secs)
