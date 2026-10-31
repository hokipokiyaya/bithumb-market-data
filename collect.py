import json, urllib.request, datetime, pathlib, time, sys
UTC=datetime.timezone.utc
KST=datetime.timezone(datetime.timedelta(hours=9))
MARKETS=['KRW-BTC','KRW-ENS','KRW-KAIA','KRW-USDT']
BASE='https://api.bithumb.com/v1'
def fetch(path):
    req=urllib.request.Request(BASE+path,headers={'User-Agent':'MarketVerification/1.0','Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=15) as r:
        if r.status!=200 or 'json' not in r.headers.get('Content-Type','').lower():raise ValueError('Invalid response')
        return json.load(r)
def iso_ms(ms):return datetime.datetime.fromtimestamp(ms/1000,UTC).astimezone(KST).isoformat()
def main():
    start=datetime.datetime.now(UTC)
    tickers=fetch('/ticker?markets='+','.join(MARKETS))
    by={t['market']:t for t in tickers}
    if set(by)!=set(MARKETS):raise ValueError('Missing ticker markets')
    result={'source':'Bithumb official public API','requested_at_kst':start.astimezone(KST).isoformat(),'collected_at_kst':None,'markets':{},'status':'ok'}
    for market in MARKETS:
        t=by[market];p=float(t['trade_price']);trade_ms=int(t['trade_timestamp']);server_ms=int(t['timestamp'])
        if p<=0 or trade_ms<=0 or server_ms<=0:raise ValueError('Invalid ticker '+market)
        age=(datetime.datetime.now(UTC).timestamp()*1000-trade_ms)/1000
        if age < -60:raise ValueError('Future trade timestamp '+market)
        data={'trade_price_krw':p,'trade_at_kst':iso_ms(trade_ms),'ticker_at_kst':iso_ms(server_ms),'trade_age_seconds':round(age,1),'stale_over_180s':age>180,'candles':{}}
        for unit in (15,60,240):
            rows=fetch(f'/candles/minutes/{unit}?market={market}&count=200')
            if not isinstance(rows,list) or not rows:raise ValueError('No candles '+market)
            out=[]
            for c in rows:
                ts=datetime.datetime.fromisoformat(c['candle_date_time_utc']).replace(tzinfo=UTC)
                end=ts+datetime.timedelta(minutes=unit)
                if end>datetime.datetime.now(UTC):continue
                out.append({'start_kst':ts.astimezone(KST).isoformat(),'end_kst':end.astimezone(KST).isoformat(),'open':c['opening_price'],'high':c['high_price'],'low':c['low_price'],'close':c['trade_price'],'volume':c['candle_acc_trade_volume']})
            if not out:raise ValueError('No completed candles '+market)
            data['candles'][str(unit)]=out
            time.sleep(.12)
        result['markets'][market]=data
    result['collected_at_kst']=datetime.datetime.now(KST).isoformat()
    dest=pathlib.Path('public/latest.json');dest.parent.mkdir(parents=True,exist_ok=True)
    tmp=dest.with_suffix('.tmp');tmp.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(dest)
    print('SUCCESS',result['collected_at_kst'],{k:v['trade_price_krw'] for k,v in result['markets'].items()})
if __name__=='__main__':
    try:main()
    except Exception as e:
        print('FAILED: no new latest.json written:',repr(e),file=sys.stderr)
        sys.exit(1)
