import fs from 'node:fs/promises';
import {Workbook,SpreadsheetFile} from '@oai/artifact-tool';
const [input,output,previewDir,language='zh']=process.argv.slice(2);
const headers={id:'编号',job_id:'岗位编号',company:'公司',title:'岗位',location:'地点',url:'岗位链接',relevance:'方向相关性',relevance_reason:'相关性依据',fit:'个人匹配',fit_reason:'匹配依据与注意事项',published_at:'发布日期',application_status:'投递状态',first_seen:'首次发现时间（UTC）',recruiting_status:'招聘状态',verification_status:'核验状态',mode:'评估模式',requirements:'要求与证据',sources:'来源链接',kind:'来源类型',outcome:'观察结论',checked_at:'核验时间（UTC）',evidence:'来源证据',method:'核验方式',excluded_reason:'排除原因',jd_completeness:'JD完整性',jd_limitations:'JD信息限制',unknown_items:'还需确认',candidate_status:'处理建议',recruiting_summary:'招聘情况'};
const labels={skill:'技能',education:'学历',experience:'经验',full:'完整可读',partial:'部分可读',unavailable:'不可读取',DirectlyRelevant:'直接相关','Directly Relevant':'直接相关',Adjacent:'相邻方向',Exploratory:'探索方向','Not Relevant':'不相关',Strong:'较强',Partial:'部分匹配','Needs clarification':'待澄清',open:'在招',closed:'已关闭',unknown:'未知',Verified:'已核验',Unverified:'未核验',Conflict:'来源冲突',Discovery:'方向发现',Matching:'证据匹配',official:'官网',third_party:'第三方',not_applied:'未投递',saved:'已收藏',applied:'已投递',interviewing:'面试中',offer:'已获Offer',rejected:'被拒绝',dismissed:'不再考虑',withdrawn:'已撤回',Met:'满足',Unknown:'未知','Not Met':'不满足',Mandatory:'必备',Preferred:'优先',Contextual:'背景信息'};
const enumFields=new Set(['relevance','fit','application_status','recruiting_status','verification_status','mode','kind','outcome','jd_completeness']);
const tr=v=>language==='zh'?(labels[v]??v):v;
if(!input||!output)throw new Error('Usage: node export.mjs export.json jobs.xlsx [preview-dir] [zh|en]');
const data=JSON.parse(await fs.readFile(input,'utf8'));
const wb=Workbook.create();
const names=['Recommended','All Jobs','Application Tracker','Verification Log'];
const defaults={Recommended:['id','company','title','location','url','relevance','recruiting_status','verification_status','application_status'], 'All Jobs':['id','company','title','location','url'], 'Application Tracker':['id','url','company','title','application_status'], 'Verification Log':['job_id','url','kind','outcome','checked_at','evidence','method']};
for (const name of names){
 const rows=data[name]||[];
 const main=name==='All Jobs'||name==='Recommended';
 const view=['id','company','title','location','candidate_status','recruiting_summary','url','fit_reason','unknown_items','application_status','published_at'];
 const keys=main?view:(rows.length?Object.keys(rows[0]):defaults[name]);
 const requirements=rows.flatMap(r=>{
  try{return JSON.parse(r.requirements||'[]').map(q=>({job:r.id,...q}));}catch{return [];}
 });
 const sheet=wb.worksheets.add(name);sheet.showGridLines=false;
 const values=[keys.map(k=>language==='zh'?(headers[k]??k):k),...rows.map(r=>keys.map(k=>{
  let v=r[k]??null;
  if(enumFields.has(k)&&typeof v==='string')v=tr(v);
  if(k==='requirements'&&typeof v==='string'&&language==='zh'){
   try{const reqs=JSON.parse(v);if(Array.isArray(reqs))v=reqs.map(r=>`${r.evidence||r.key}；${tr(r.criticality)}；判断：${tr(r.assessment||'Unknown')}；用户证据：${r.candidate_evidence||'未提供'}`).join('\n');}catch{}
  }
  if(['published_at','first_seen','checked_at'].includes(k)&&v)return new Date(v);
  if(typeof v==='object'&&v!==null)v=JSON.stringify(v);
  return typeof v==='string'&&/^[=+@-]/.test(v)?"'"+v:v;
 }))];
 const range=sheet.getRangeByIndexes(0,0,values.length,keys.length);range.values=values;
 range.format.font={name:'Arial',size:10};range.format.verticalAlignment='center';range.format.columnWidth=22;range.format.rowHeight=30;
 const header=sheet.getRangeByIndexes(0,0,1,keys.length);header.format.fill='#263E59';header.format.font={name:'Arial',size:10,bold:true,color:'#FFFFFF'};header.format.rowHeight=34;
 sheet.freezePanes.freezeRows(1);
 keys.forEach((k,i)=>{
  const col=sheet.getRangeByIndexes(0,i,values.length,1);
  if(['url','sources'].includes(k))col.format.columnWidth=65;
  else if(['title','relevance_reason','fit_reason','evidence','requirements','method','jd_limitations','unknown_items'].includes(k)){col.format.columnWidth=65;col.format.wrapText=true;}
  if(['published_at','first_seen','checked_at'].includes(k))col.setNumberFormat('yyyy-mm-dd hh:mm');
  if(k==='id')col.format.columnWidth=10;
 });
 if(rows.length)sheet.tables.add(sheet.getRangeByIndexes(0,0,values.length,keys.length),true,name.replaceAll(' ','')+'Table');
 if(name==='Application Tracker'&&rows.length){const ix=keys.indexOf('application_status');const editable=sheet.getRangeByIndexes(1,ix,rows.length,1);editable.format.fill='#FFF2CC';editable.dataValidation={rule:{type:'list',values:['not_applied','saved','applied','interviewing','offer','rejected','dismissed','withdrawn'].map(tr)}};}
 range.format.autofitRows();
 if(main){
  for(let r=0;r<rows.length;r++){
   const lines=Math.max(1,...['fit_reason','unknown_items'].map(k=>String(rows[r][k]??'').split('\n').reduce((sum,line)=>sum+Math.max(1,Math.ceil([...line].reduce((n,ch)=>n+(/[\u2E80-\uFFFF]/.test(ch)?2:1),0)/65)),0)));
   sheet.getRangeByIndexes(r+1,0,1,keys.length).format.rowHeight=Math.max(30,lines*13+10);
  }
  const matching=rows.some(r=>r.mode==='Matching');
  const note=language==='zh'?(matching?'本次按简历经历对照；推荐可含第三方岗位；招聘状态待核实表示尚未确认当前在招，请结合核验日志查看。':'本次按岗位方向整理；尚未判断个人适合程度。'):(matching?'Compared against resume evidence; missing skills remain unknown.':'Direction discovery only; personal fit not assessed.');
  sheet.getCell(values.length+1,0).values=[[note]];
 }
 // Keep the 20-job view compact; full evidence is a separate ID-linked table on All Jobs.
 if(name==='All Jobs'&&requirements.length){
  const start=values.length+3;
  sheet.getCell(start-1,0).values=[[language==='zh'?'逐项要求与证据（按岗位编号关联）':'Requirement evidence by job ID']];
  sheet.getCell(start-1,0).format.font={name:'Arial',size:12,bold:true};
  const detailHeaders=language==='zh'?['编号','要求','JD依据','要求性质','判断','用户证据','硬性排除','要求类别','证据链接']:['id','requirement','JD evidence','criticality','assessment','candidate evidence','hard exclusion','kind','url'];
  const matrix=[detailHeaders,...requirements.map(q=>[q.job,q.key,q.evidence,tr(q.criticality),tr(q.assessment||'Unknown'),q.candidate_evidence||(language==='zh'?'未提供':'Not provided'),language==='zh'?(q.hard_exclusion?'是':'否'):!!q.hard_exclusion,tr(q.kind),q.url].map(v=>typeof v==='string'&&/^[=+@-]/.test(v)?"'"+v:v))];
  const details=sheet.getRangeByIndexes(start,0,matrix.length,9);details.values=matrix;details.format.font={name:'Arial',size:10};details.format.verticalAlignment='top';details.format.wrapText=true;
  const h=sheet.getRangeByIndexes(start,0,1,9);h.format.fill='#263E59';h.format.font={name:'Arial',size:10,bold:true,color:'#FFFFFF'};
  sheet.getRangeByIndexes(start,8,matrix.length,1).format.wrapText=false;
  sheet.tables.add(details,true,'RequirementEvidenceTable');details.format.autofitRows();
  for(let r=1;r<matrix.length;r++){
   const widths=[10,22,65,22,22,22,22,22];
   const lines=Math.max(...matrix[r].slice(0,8).map((v,c)=>String(v??'').split('\n').reduce((sum,line)=>sum+Math.max(1,Math.ceil([...line].reduce((n,ch)=>n+(/[\u2E80-\uFFFF]/.test(ch)?2:1),0)/widths[c])),0)));
   sheet.getRangeByIndexes(start+r,0,1,9).format.rowHeight=Math.max(30,lines*13+10);
  }
 }
}
wb.recalculate();
const check=await wb.inspect({kind:'table',range:'Recommended!A1:I4',include:'values',tableMaxRows:4,tableMaxCols:9,maxChars:2500});console.log(check.ndjson);
if(previewDir){await fs.mkdir(previewDir,{recursive:true});for(const name of names){const img=await wb.render({sheetName:name,range:name==='Verification Log'?'A1:G5':name==='Application Tracker'?'A1:E4':'A1:I4',scale:1,format:'png'});await fs.writeFile(`${previewDir}/${name.replaceAll(' ','-')}.png`,new Uint8Array(await img.arrayBuffer()));}}
const out=await SpreadsheetFile.exportXlsx(wb);await out.save(output);console.log('Exported '+output);
