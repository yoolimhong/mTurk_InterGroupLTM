#!/usr/bin/python
from boto.mturk.connection import MTurkConnection
from boto.mturk.question import ExternalQuestion
import boto.mturk.qualification as mtqu
import boto.mturk.price as mtcPrice
import json, os
import pandas as pd

## CCLAB ##
#ACCESS_ID = 'xxxxx'
#SECRET_KEY = 'ask lab member'

HOST = 'mechanicalturk.sandbox.amazonaws.com' # Use this to post to the sandbox
#HOST = 'mechanicalturk.amazonaws.com' # Use this to post to the real mTurk

def Bank():
  mtc = MTurkConnection(aws_access_key_id=ACCESS_ID,
                        aws_secret_access_key=SECRET_KEY,
                        host=HOST)
  print 'Funds: '
  print mtc.get_account_balance()

Bank()

def PostHits():
  mtc = MTurkConnection(aws_access_key_id=ACCESS_ID,
                        aws_secret_access_key=SECRET_KEY,
                        host=HOST)

  q = ExternalQuestion(external_url = "https://paulscotti.github.io/mturk/ContLTMBlocked90", frame_height=675)
  keywords = ['memory', 'psychology', 'game', 'attention', 'experiment', 'research']
  title = 'Memorize the colors of objects! (Psychology Experiment, 1.5 hours)'
  experimentName = 'Cont_LTM_90'
  description = 'Research study involving color memory.'
  pay = 9.00

  qualifications = mtqu.Qualifications()
  qualifications.add(mtqu.PercentAssignmentsApprovedRequirement('GreaterThanOrEqualTo', 98))
  qualifications.add(mtqu.NumberHitsApprovedRequirement('GreaterThanOrEqualTo', 1000))
  qualifications.add(mtqu.LocaleRequirement("EqualTo", "US"))
  qualifications.add(mtqu.Requirement('38XLDN1M8DBWG1FPHU43ZCVTZ4T3DT','DoesNotExist','','DiscoverPreviewAndAccept')) # No prior workers of ours
  qualifications.add(mtqu.Requirement('2F1QJWKUDD8XADTFD2Q0G6UTO95ALH','Exists','','DiscoverPreviewAndAccept')) # Masters only

  theHIT = mtc.create_hit(question=q,
                          lifetime=2 * 60 * 60, # 2 hours
                          max_assignments=1, #needs to be less than 10 else additional fees
                          title=title,
                          description=description,
                          keywords=keywords,
                          qualifications=qualifications,
                          reward=pay,
                          duration=180 * 60, #3 hours (HIT won't be accepted if they go over time)
                          approval_delay=1 * 60 * 60, # 1 hours
                          annotation=experimentName)

  assert(theHIT.status == True)
  print theHIT
  print theHIT[0].HITId

#PostHits()

def AwardHits():
  mtc = MTurkConnection(aws_access_key_id=ACCESS_ID,
                        aws_secret_access_key=SECRET_KEY,
                        host=HOST)

  # this finds our json files, you need to have already downloaded them and put them in a folder
  path_to_json = '/Users/scotti.5/Dropbox/Shared Lab Folder/Experiments/Contextual_LTM/mTurk Analysis/newData'
  json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

  # here I define my pandas Dataframe with the columns I want to get from the json
  jsons_data = pd.DataFrame(columns=['WORKERID','Bonus'])

  # we need both the json and an index number so use enumerate()
  for index, js in enumerate(json_files):
      with open(os.path.join(path_to_json, js)) as json_file:
            json_text = json.load(json_file)
            subjID =[]
            cashprize=[]
            assignmentNum=[]
            # here you need to know the layout of your json and each json has to have
            subjID = json_text['WORKERID']
            print(subjID)
            cashprize = json_text['Bonus']
            assignmentNum = json_text['ASSIGNMENTID']
            # here I push a list of data into a pandas DataFrame at row given by 'index'
            jsons_data.loc[index] = [subjID,cashprize]

            subjID = jsons_data.loc[0,'WORKERID']
            cashprize = jsons_data.loc[0,'Bonus']

            # block worker from future HITs
            mtc.assign_qualification('38XLDN1M8DBWG1FPHU43ZCVTZ4T3DT',subjID);

            bonusHIT = mtc.grant_bonus(worker_id=subjID,
                                  assignment_id=assignmentNum,
                                  bonus_price=mtcPrice.Price(amount = cashprize),
                                  reason='Bonus awarded based on memory experiment performance')

            assert(bonusHIT.status == True)
            print bonusHIT

#AwardHits()

def ManualReward():
  mtc = MTurkConnection(aws_access_key_id=ACCESS_ID,
                        aws_secret_access_key=SECRET_KEY,
                        host=HOST)

  q = ExternalQuestion(external_url = "https://paulscotti.github.io/mturk/RewardPage", frame_height=675)
  keywords = ['compensation','experiment', 'research']
  title = 'Compensation for Cont_LTM color experiment'
  experimentName = 'Cont_LTM_Reward'
  description = 'Compensating a previous worker of the Cont_LTM study.'
  pay = 10.27

  #for adding new people
  #mtc.assign_qualification('35GMP5037Q9KDB285EZ1DGC38JE39C','A1N1EF0MIRSEZZ');

  qualifications = mtqu.Qualifications()
  qualifications.add(mtqu.Requirement('35GMP5037Q9KDB285EZ1DGC38JE39C','Exists','','DiscoverPreviewAndAccept'))

  rewardHIT = mtc.create_hit(question=q,
                          lifetime=12 * 60 * 60, #12 hours
                          max_assignments=1, #needs to be less than 10 else additional fees
                          title=title,
                          description=description,
                          keywords=keywords,
                          qualifications=qualifications,
                          reward=pay,
                          duration=10 * 60, #10 minutes (HIT won't be accepted if they go over time)
                          approval_delay=12 * 60 * 60, # 12 hours
                          annotation=experimentName)

  assert(rewardHIT.status == True)
  print rewardHIT
  print rewardHIT[0].HITId

#ManualReward()

Bank()
