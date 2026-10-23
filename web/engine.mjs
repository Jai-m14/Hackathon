export const STAGES=['Seed','Series A','Series B','Series C+','Pre-IPO'];
export const WEIGHTS={valuation:35,survival:25,backing:20,tech:10,stage:10};
export function hydrate(payload){
 const priority=new Map(payload.referencePortfolio.map((id,i)=>[id,i]));
 return payload.rows.map((row,i)=>{
  const o=Object.fromEntries(payload.columns.map((c,j)=>[c,row[j]]));
  return {uid:String(i),id:o.Company_ID,domain:o.Domain,country:o['Headquarters (Country)']||'Unknown',city:o['Headquarters (City)']||'Not recorded',
   stage:o.Funding_Stage,cohort:o['Y Combinator Year'],session:o['Y Combinator Session'],description:o.Description||'No description recorded.',categories:o.Categories||'Not recorded',
   funding:o.Total_Raised_USD_Millions,fundingRaw:o['Amounts raised in different funding rounds'],investors:o.Investor_Count,tier1:o.Tier1_Investor_Count,founders:o.Founder_Count,
   founderNames:o.Founders||'Not recorded',investorNames:o.Investors||'Not recorded',website:o.Website,status:o.Status,multiple:o.Observed_Multiple,
   peerMultiple:o.Peer_Multiple,fairValue:o.Fair_Value_USD_Millions,upside:o.Upside_to_Fair_Value,years:o.Years_Since_YC,score:o.Risk_Adjusted_Score,
   parts:{valuation:o.Valuation_Score,survival:o.Survival_Score,backing:o.Backing_Score,tech:o.Tech_Score,stage:o.Stage_Score},
   priority:priority.get(o.Company_ID)??100000+i,order:i};
 });
}
export function filterRecords(records,{country='all',stage='all',domain='all',search='',sort='score'}={}){
 const t=search.trim().toLowerCase();
 return records.filter(r=>r.status==='Operating'&&(country==='all'||r.country===country)&&(domain==='all'||r.domain===domain)&&(stage==='all'||r.stage===stage)&&
  (!t||[r.id,r.city,r.country,r.domain,r.description].some(v=>String(v).toLowerCase().includes(t))))
  .sort((a,b)=>(sort==='funding'?b.funding-a.funding:sort==='backers'?b.investors-a.investors:sort==='gap'?b.upside-a.upside:b.score-a.score)||a.priority-b.priority||a.order-b.order);
}
export function allocationInputs(records){
 if(!records.length)return [];
 const funding=records.map(r=>Math.log1p(r.funding*1000)),backers=records.map(r=>Math.log1p(r.investors));
 const meanF=funding.reduce((a,b)=>a+b,0)/records.length,meanB=backers.reduce((a,b)=>a+b,0)/records.length;
 return records.map((r,i)=>{const fundingFactor=funding[i]/meanF,sizeFactor=backers[i]/meanB;
  const scale=Math.sqrt(fundingFactor*sizeFactor);return {record:r,fundingFactor,sizeFactor,scale,allocationScore:Math.max(r.score,.01)*scale};});
}
export function allocate(records,budget=100000,cashRate=.1,cap=.25,floor=.04){
 if(!Number.isFinite(budget)||budget<=0||cashRate<0||cashRate>1||cap<=0||cap>1||floor<0||floor>cap)throw new Error('Invalid capital policy');
 const inputs=allocationInputs(records);
 if(!inputs.length)return {budget,positions:[],cash:budget,cashWeight:1,invested:0};
 if(inputs.some(p=>!Number.isFinite(p.allocationScore)||p.allocationScore<=0))throw new Error('Missing allocation inputs');
 const target=Math.min(1-cashRate,records.length*cap);
 if(records.length*floor>target+1e-12)throw new Error('Position floor exceeds the available investment budget');
 const sumAt=x=>inputs.reduce((s,p)=>s+Math.min(cap,Math.max(floor,x*p.allocationScore)),0);
 let lo=0,hi=1;while(sumAt(hi)<target-1e-12)hi*=2;
 for(let i=0;i<100;i++){const mid=(lo+hi)/2;if(sumAt(mid)<target)lo=mid;else hi=mid;}
 const weights=inputs.map(p=>Math.min(cap,Math.max(floor,(lo+hi)/2*p.allocationScore)));
 const maximum=Math.floor(cap*budget+1e-8),minimum=Math.ceil(floor*budget-1e-8);
 const dollars=weights.map(w=>Math.max(minimum,Math.min(maximum,Math.round(w*budget))));
 const targetDollars=Math.floor(target*budget+1e-8);let delta=targetDollars-dollars.reduce((a,b)=>a+b,0);
 // Match team whole-dollar rounding, correcting the first position within bounds.
 // A sparse mandate retains cash rather than adding excess to a capped company.
 for(let i=0;delta!==0&&i<inputs.length;i++){
  const change=delta>0?Math.min(delta,maximum-dollars[i]):Math.max(delta,minimum-dollars[i]);dollars[i]+=change;delta-=change;
 }
 const invested=dollars.reduce((a,b)=>a+b,0),cash=Math.round((budget-invested)*100)/100;
 return {budget,positions:inputs.map((p,i)=>({...p,weight:dollars[i]/budget,amount:dollars[i]})),invested,cash,cashWeight:cash/budget};
}
export function selectPortfolio(records,mandate){
 const eligible=filterRecords(records,mandate);
 if(mandate.selection==='domain'){
  const seen=new Set();return eligible.filter(r=>{if(seen.has(r.domain))return false;seen.add(r.domain);return true;}).slice(0,mandate.positions||10);
 }
 return eligible.slice(0,mandate.positions||10);
}
export function validateResearchRows(rows){return rows.map(r=>({...r,company_name:String(r.company_name||r.Company_ID||r.Company||'').trim()})).filter(r=>r.company_name&&r.company_name.toUpperCase()!=='CASH'&&r.overall_sentiment_score!==null&&r.overall_sentiment_score!==undefined&&String(r.overall_sentiment_score).trim()!==''&&Number.isFinite(Number(r.overall_sentiment_score))&&Math.abs(Number(r.overall_sentiment_score))<=1);}
export function parseCSV(text){const rows=[];let row=[],cell='',quoted=false;for(let i=0;i<text.length;i++){const c=text[i];if(c==='"'){if(quoted&&text[i+1]==='"'){cell+='"';i++;}else quoted=!quoted;}else if(c===','&&!quoted){row.push(cell);cell='';}else if((c==='\n'||c==='\r')&&!quoted){if(c==='\r'&&text[i+1]==='\n')i++;row.push(cell);if(row.some(v=>v.length))rows.push(row);row=[];cell='';}else cell+=c;}if(quoted)throw new Error('Unclosed quoted field');if(cell||row.length){row.push(cell);rows.push(row);}if(!rows.length)return [];const headers=rows.shift().map(h=>h.replace(/^\uFEFF/,'').trim());if(new Set(headers).size!==headers.length)throw new Error('Duplicate CSV headers');if(rows.some(r=>r.length!==headers.length))throw new Error('Inconsistent CSV row width');return rows.map(r=>Object.fromEntries(headers.map((h,i)=>[h,r[i]])));}
