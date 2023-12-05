import os, pprint, datetime, logging
from todoist_api_python.api import TodoistAPI
from pathlib import Path
import __main__

auth_token = os.getenv('TODOIST_AUTH_TOKEN')
api = TodoistAPI(auth_token)

print(f"{auth_token=}")

pp = pprint.PrettyPrinter(indent=2)

logging.basicConfig(
    level=logging.INFO,
    format="\n[%(levelname)s] %(asctime)s -- %(filename)s on line %(lineno)s\n\tFunction name: %(funcName)s\n\tMessage: %(message)s\n",
    datefmt='%B-%d-%Y %H:%M:%S',
    filename=f"./logs/{datetime.datetime.today().strftime('%Y-%m-%d')}_{Path(__main__.__file__).stem}.log",
    filemode='a'
)

if __name__ == '__main__':
    task_contents = []
    try:
        all_tasks = api.get_tasks(filter="#🏠 Chores")
        
        for task in all_tasks:
            task_contents.append(task.content)
        
        for task in all_tasks:
            
            if task.id == '6350698503':
                
                due_date = task.due.date
                litter_due_date = datetime.date(int(due_date[0:4]), int(due_date[5:7]), int(due_date[8:10]))
                scoop_due_date  = datetime.date(int(due_date[0:4]), int(due_date[5:7]), int(due_date[8:10]) - 3)
                scoop_due_datetime  = datetime.datetime(int(due_date[0:4]), int(due_date[5:7]), int(due_date[8:10]) - 3, 20)
                
                if scoop_due_date > datetime.date.today():
                    logging.info(f"{litter_due_date=} {scoop_due_date=}")
                    logging.info('scoop date is in the future')
                    if 'Scoop litter' in task_contents:
                        logging.info('Scoop task already in task list')
                    else:
                        logging.info('Scoop task not in task list')
                        task = api.add_task(
                            content="Scoop litter",
                            due_string=f"{scoop_due_datetime.strftime('%B %d at %-I %p')}",
                            due_lang="en",
                            priority=2,
                            project_id=2300556566,
                        )
                else:
                    logging.info(f"{litter_due_date=} {scoop_due_date=}")
                    logging.info('scoop date is in the past')

    except Exception as error:
        logging.error(error, exc_info=True) # test for webhook