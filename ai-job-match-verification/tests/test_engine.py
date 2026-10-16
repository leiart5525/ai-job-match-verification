import unittest, sys, copy, tempfile, subprocess, json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'skills/ai-job-match-verification/scripts'))
import jobmatch as m

def job(i=1,**extra):
 j={'company':'Synthetic Co','title':f'AI Product {i}','location':'Test City','url':f'https://example.org/jobs/{i}','relevance':'Directly Relevant','relevance_reason':'Synthetic AI product responsibilities','requirements':[],'observations':[]};j.update(extra);return j

def requirement(key='Python',**extra):
 r={'key':key,'kind':'skill','criticality':'Mandatory','evidence':'Synthetic mandatory requirement','url':'https://example.org/jobs/1','decision_impact':True,'assessment':'Unknown'};r.update(extra);return r

def observation(outcome='open',kind='official',url='https://example.org/jobs/1',**extra):
 o={'url':url,'kind':kind,'outcome':outcome,'checked_at':m.now(),'evidence':'Synthetic application link' if outcome=='open' else 'Synthetic observation','method':'synthetic'};o.update(extra);return o

class Acceptance(unittest.TestCase):
 def setUp(self):self.s=m.empty()
 def test_intake_missing_cannot_start(self):
  self.s['profile']={'target':'策略增长运营','locations':['上海']}
  result=m.intake(self.s);self.assertFalse(result['ready']);self.assertEqual(result['missing_required'],['experience_years','education']);self.assertIn('salary',result['optional_to_offer'])
 def test_intake_complete_no_optional_skills_needed(self):
  self.s['profile']={'target':'策略增长运营','locations':['上海'],'experience_years':3,'education':'本科'}
  self.assertTrue(m.intake(self.s)['ready']);self.assertEqual(m.mode(self.s),'Discovery')
 def test_intake_zero_years_valid_unknown_education_not_valid(self):
  self.s['profile']={'target':'不限运营方向','locations':['全国不限'],'experience_years':0,'education':'高中'};self.assertTrue(m.intake(self.s)['ready'])
  self.s['profile']['education']='Unknown';self.assertFalse(m.intake(self.s)['ready'])
  self.s['profile']['education']='本科';self.s['profile']['experience_years']=True;self.assertFalse(m.intake(self.s)['ready'])
 def test_coverage_short_list_is_not_market_exhaustion(self):
  m.ingest(self.s,{'jobs':[job(i) for i in range(4)]});c=m.coverage(self.s);self.assertEqual(c['unique_jobs'],4);self.assertEqual(len(c['warnings']),2)
  self.s['search_log']=[{'source_id':'a','kind':'official','outcome':'searched'},{'source_id':'b','kind':'third_party','outcome':'searched'}];c=m.coverage(self.s);self.assertEqual(c['channels_searched'],['official','third_party']);self.assertEqual(len(c['warnings']),1)
 def test_intake_cli_after_persistence(self):
  with tempfile.TemporaryDirectory() as td:
   state=Path(td)/'state.json';batch=Path(td)/'profile.json';script=Path(m.__file__)
   batch.write_text(json.dumps({'profile':{'target':'策略增长运营','locations':['上海'],'experience_years':4,'education':'本科'}}))
   subprocess.run([sys.executable,str(script),'--state',str(state),'ingest',str(batch)],check=True,capture_output=True)
   result=subprocess.run([sys.executable,str(script),'--state',str(state),'intake'],check=True,capture_output=True,text=True);self.assertTrue(json.loads(result.stdout)['ready'])
 def test_cli_blocks_outputs_before_required_intake(self):
  with tempfile.TemporaryDirectory() as td:
   state=Path(td)/'state.json';state.write_text(json.dumps(m.empty()));script=Path(m.__file__)
   for command in (['recommend'],['clarify'],['export-data',str(Path(td)/'out.json')]):
    result=subprocess.run([sys.executable,str(script),'--state',str(state),*command],capture_output=True,text=True);self.assertNotEqual(result.returncode,0);self.assertIn('必要信息未齐全',result.stderr)
   self.assertFalse((Path(td)/'out.json').exists())
 def test_chinese_tracker_conflicts_without_overwrite(self):
  m.ingest(self.s,{'jobs':[job()]});pending=m.import_tracker(self.s,[{'编号':'J001','职位链接':'https://example.org/jobs/1','投递状态':'被拒绝'}]);self.assertEqual(pending[0]['incoming'],'rejected');self.assertEqual(self.s['jobs'][0]['application_status'],'not_applied')
 def test_complete_profile_can_export_via_cli(self):
  with tempfile.TemporaryDirectory() as td:
   s=m.empty();s['profile']={'target':'增长运营','locations':['上海'],'experience_years':4,'education':'本科'}
   m.ingest(s,{'jobs':[job()]});state=Path(td)/'state.json';state.write_text(json.dumps(s));out=Path(td)/'out.json'
   result=subprocess.run([sys.executable,str(Path(m.__file__)),'--state',str(state),'export-data',str(out)],capture_output=True,text=True);self.assertEqual(result.returncode,0,result.stderr);self.assertEqual(len(json.loads(out.read_text())['All Jobs']),1)
 def test_partial_jd_cannot_claim_strong_overall_fit(self):
  with self.assertRaises(ValueError):m.validate_job(job(fit='Strong',fit_reason='Only a SQL match',jd_completeness='partial'))
  m.validate_job(job(fit='Partial',fit_reason='Only documented parts assessed',jd_completeness='partial'))
 def test_official_display_url_reingest_does_not_duplicate(self):
  third='https://example.net/board/1';official='https://example.org/jobs/1'
  incoming=job(url=third,observations=[observation(url=official)])
  m.ingest(self.s,{'jobs':[incoming]});m.ingest(self.s,{'jobs':[incoming]})
  self.assertEqual(self.s['jobs'][0]['url'],official);self.assertIn(official,self.s['jobs'][0]['urls'])
  m.update_status(self.s,'J001','rejected');m.ingest(self.s,{'jobs':[job(url=official)]})
  self.assertEqual(len(self.s['jobs']),1);self.assertEqual(self.s['jobs'][0]['id'],'J001');self.assertEqual(self.s['jobs'][0]['application_status'],'rejected')
 def test_legacy_display_url_missing_from_aliases_still_dedups(self):
  m.ingest(self.s,{'jobs':[job(url='https://example.net/board/1')]});self.s['jobs'][0]['url']='https://example.org/jobs/1'
  m.ingest(self.s,{'jobs':[job(url='https://example.org/jobs/1')]});self.assertEqual(len(self.s['jobs']),1)
 def test_replay_does_not_invent_new_verification_events(self):
  batch={'jobs':[job(observations=[observation()])]};m.ingest(self.s,batch);m.ingest(self.s,batch)
  self.assertEqual(len(self.s['log']),1);self.assertEqual(len(self.s['jobs'][0]['observations']),1)
  changed=job(observations=[observation('unknown',evidence='New failed check')]);m.ingest(self.s,{'jobs':[changed]});self.assertEqual(len(self.s['log']),2)
 def test_evidence_backed_third_party_recommended_without_official_match(self):
  m.ingest(self.s,{'jobs':[job(1,observations=[observation(kind='third_party'),observation('unknown',url='https://example.org/official/1')]),job(2,observations=[observation(url='https://example.org/jobs/2')])]})
  self.assertEqual([j['id'] for j in m.recommend(self.s)],['J001','J002']);self.assertEqual(m.status(self.s['jobs'][0]),('unknown','Unverified'))
  data=m.export_data(self.s);self.assertEqual(len(data['All Jobs']),2);self.assertEqual(len(data['Recommended']),2);self.assertEqual(data['All Jobs'][0]['candidate_status'],'可考虑，招聘状态待核实')
 def test_local_priority_expands_and_source_override_wins(self):
  self.s['search_policy']={'priority_groups':['阿里系','字节／飞书','Kimi／月之暗面'],'allow_expansion':True}
  self.s['source_overrides']['kimi']={'enabled':False}
  plan=m.search_plan(self.s);self.assertEqual(plan['priority_groups'],self.s['search_policy']['priority_groups']);self.assertTrue(plan['allow_expansion']);self.assertNotIn('kimi',plan['sources'])
  self.assertEqual(m.search_plan(m.empty())['priority_groups'],[])
 def test_no_observation_is_not_default_recommendation(self):
  m.ingest(self.s,{'jobs':[job()]});self.assertEqual(m.recommend(self.s),[])
 def test_unknown_candidate_skill_does_not_block_open_role(self):
  m.ingest(self.s,{'jobs':[job(requirements=[requirement()],observations=[observation()])]});self.assertEqual(len(m.recommend(self.s)),1)
 def test_unknown_retained(self):
  m.ingest(self.s,{'jobs':[job(requirements=[requirement()])]});self.assertEqual(len(m.recommend(self.s,include_unverified=True)),1)
  with self.assertRaises(ValueError):m.validate_job(job(requirements=[requirement(hard_exclusion=True)]))
 def test_modes_and_no_percentage(self):
  m.ingest(self.s,{'jobs':[job(fit='Strong',fit_reason='Synthetic reason',jd_completeness='full')]});self.assertNotIn('fit',m.recommend(self.s,include_unverified=True)[0])
  self.s['profile']={'matching_ready':True};self.assertEqual(m.mode(self.s),'Discovery')
  self.s['profile']['experience']=[{'summary':'Built AI products','evidence':'Synthetic conversation'}];self.assertEqual(m.mode(self.s),'Matching')
 def test_conflict_official_priority(self):
  j=job(observations=[observation('closed'),observation('open','third_party','https://example.net/1')]);self.assertEqual(m.status(j),('closed','Conflict'))
 def test_404_not_closed(self):
  j=job(observations=[observation(),observation('unknown',evidence='HTTP 404')]);self.assertEqual(m.status(j)[0],'unknown')
 def test_stale_evidence(self):
  from datetime import datetime,timezone,timedelta
  j=job(observations=[observation(checked_at=(datetime.now(timezone.utc)-timedelta(days=10)).isoformat())]);self.assertEqual(m.status(j),('unknown','Unverified'))
 def test_rejected_persists(self):
  m.ingest(self.s,{'jobs':[job()]});m.update_status(self.s,'J001','rejected');m.ingest(self.s,{'jobs':[job(observations=[observation()])]});self.assertEqual(m.recommend(self.s,include_unverified=True),[]);self.assertEqual(self.s['jobs'][0]['id'],'J001')
 def test_dedup_and_separate_locations(self):
  m.ingest(self.s,{'jobs':[job(),job(url='https://example.org/jobs/1?utm_source=x'),job(2,title='AI Product 1',location='Elsewhere')]});self.assertEqual(len(self.s['jobs']),2)
  m.ingest(self.s,{'jobs':[job(url='https://example.net/1',merge_into='J001')]});self.assertEqual(len(self.s['jobs']),2);self.assertEqual(len(self.s['jobs'][0]['urls']),3)
 def test_300_high_value_questions(self):
  jobs=[job(i,requirements=[requirement('Python' if i<150 else 'Java')]+([requirement('LLM',criticality='Contextual')] if i<5 else [])) for i in range(300)]
  m.ingest(self.s,{'jobs':jobs});out=m.clarify(self.s);self.assertEqual(out['action'],'Ask');self.assertEqual({x['key'] for x in out['questions']},{'Python','Java'})
  self.s['questions']={'Python':{'result':'skipped'},'Java':{'result':'asked'}};self.assertEqual(m.clarify(self.s)['action'],'Refine')
  self.s['profile']['broad_discovery']=True;self.assertEqual(m.clarify(self.s)['action'],'Proceed')
 def test_known_skills_no_ask(self):
  m.ingest(self.s,{'jobs':[job(i,requirements=[requirement(assessment='Met',candidate_evidence='Synthetic commercial Python project')]) for i in range(10)]});self.s['profile']['skills']={'Python':{'state':'Met','evidence':'Synthetic project'}};self.assertEqual(m.clarify(self.s)['questions'],[])
 def test_assessed_experience_not_asked_again(self):
  m.ingest(self.s,{'jobs':[job(i,requirements=[requirement('用户运营经验',kind='experience',assessment='Met',candidate_evidence='Synthetic four-year user ops work')]) for i in range(5)]});self.assertEqual(m.clarify(self.s)['unknowns'],[])
 def test_general_skill_does_not_prove_jd_level(self):
  m.ingest(self.s,{'jobs':[job(i,requirements=[requirement('Python')]) for i in range(5)]});self.s['profile']['skills']={'Python':{'state':'Met','level':'learning','evidence':'Synthetic tutorial'}};self.assertEqual(m.clarify(self.s)['action'],'Ask')
 def test_education_and_mandatory(self):
  r=requirement('degree',kind='education',assessment='Not Met',candidate_evidence='Synthetic user says below required degree',hard_exclusion=True)
  with self.assertRaises(ValueError):m.validate_job(job(requirements=[r]))
  m.ingest(self.s,{'profile':{'matching_ready':True,'experience':[{'summary':'Product work','evidence':'Synthetic'}]},'jobs':[job(requirements=[r],observations=[observation()])]});self.assertEqual(m.recommend(self.s,include_unverified=True),[])
 def test_import_conflicts_no_silent_overwrite(self):
  m.ingest(self.s,{'jobs':[job()]});out=m.import_tracker(self.s,[{'id':'J900','url':'https://example.org/jobs/1','application_status':'rejected'}]);self.assertEqual(out[0]['job_id'],'J001');self.assertEqual(self.s['jobs'][0]['application_status'],'not_applied')
  self.assertEqual(m.import_tracker(self.s,[{'id':'J001','url':'https://example.net/other','application_status':'applied'}])[0]['reason'],'unmatched_url')
 def test_latest_unknown_last_and_top10(self):
  m.ingest(self.s,{'jobs':[job(i) for i in range(12)]+[job(50,published_at='2026-10-10',published_evidence='Synthetic sourced date')]});self.assertEqual(len(m.recommend(self.s,include_unverified=True)),10);self.assertEqual(m.recommend(self.s,'latest',include_unverified=True)[0]['id'],'J013')
 def test_export_four_tabs(self):
  m.ingest(self.s,{'jobs':[job()]});self.assertEqual(set(m.export_data(self.s)),{'All Jobs','Recommended','Application Tracker','Verification Log'})
 def test_official_primary_url_survives_merge(self):
  m.ingest(self.s,{'jobs':[job(observations=[observation()]),job(url='https://example.net/1',merge_into='J001')]});self.assertEqual(self.s['jobs'][0]['url'],'https://example.org/jobs/1')
 def test_export_preserves_all_rows_and_empty(self):
  self.assertEqual(m.export_data(self.s)['All Jobs'],[])
  m.ingest(self.s,{'jobs':[job(1,observations=[observation(url='https://example.org/jobs/1')]),job(2,observations=[observation(url='https://example.org/jobs/2')])]});self.assertEqual(len(m.export_data(self.s)['All Jobs']),2);self.assertEqual(len(m.export_data(self.s)['Recommended']),2)
 def test_atomic_invalid_batch(self):
  with tempfile.TemporaryDirectory() as td:
   state=Path(td)/'state.json';batch=Path(td)/'batch.json';script=Path(m.__file__)
   subprocess.run([sys.executable,str(script),'--state',str(state),'init'],check=True,capture_output=True);before=state.read_bytes()
   batch.write_text(json.dumps({'jobs':[job(),job(2,relevance='invented')]}));result=subprocess.run([sys.executable,str(script),'--state',str(state),'ingest',str(batch)],capture_output=True);self.assertNotEqual(result.returncode,0);self.assertEqual(state.read_bytes(),before)
 def test_resume_text_and_empty(self):
  with tempfile.TemporaryDirectory() as td:
   p=Path(td)/'resume.txt';out=Path(td)/'out.txt';p.write_text('Synthetic product experience');m.extract(p,out);self.assertEqual(out.read_text(),p.read_text());p.write_text('')
   with self.assertRaises(ValueError):m.extract(p,out)
if __name__=='__main__':unittest.main(verbosity=2)
