import datetime
from geoapi.models import Job

class JobManager():

    def get_job(self, job_id: str | None) -> Job | None:
        if job_id is None:
            return None
        
        job_exists = Job.objects.filter(pk=job_id).exists()
        if not job_exists:
            return None
        
        job = Job.objects.filter(pk=job_id).first()
        return job

    def update_job_progress(self, job_id: str | None, progress: int) -> bool | None:
        """
        Update the progress of a job given by the job id.

        Returns:

        True if the job progress was updated. False if the progress was not updated. 
        None if the job does not exist
        """
        job = self.get_job(job_id)
        if job is None:
            return None
        
        else:
            try:
                job.progress = progress
                job.updated_datetime = datetime.datetime.now()
                job.duration = (job.updated_datetime - job.start_datetime).total_seconds()
                job.save()
                return True
            except:
                return False
