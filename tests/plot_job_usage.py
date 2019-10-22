import matplotlib.pyplot as plt 
import seaborn as sns
import pandas as pd 

total_possible_pairings = 411522
time_per_pairing = 5


number_of_jobs = []
pairings_per_job = []
time_per_job = []
total_computing_time = []

for n_jobs in range(200, 2000):
	number_of_jobs.append(n_jobs)
	pairings_per_job.append(total_possible_pairings/n_jobs)
	time_per_job.append(total_possible_pairings/n_jobs*time_per_pairing/60)
	total_computing_time.append(n_jobs*total_possible_pairings/n_jobs*time_per_pairing/60)

df = pd.DataFrame(list(zip(number_of_jobs, pairings_per_job, time_per_job, total_computing_time)), columns=[
													"Number of submitted jobs",
													"Perturbations per job",
													"Estimated computing time per job (minutes)",
													"Total estimated computing time (minutes)"
													])

f, axes = plt.subplots(2, 1)


sns.lineplot(x="Number of submitted jobs", y="Perturbations per job", data=df, ax=axes[0])
sns.lineplot(x="Number of submitted jobs", y="Estimated computing time per job (minutes)", data=df,ax=axes[1])

plt.show()