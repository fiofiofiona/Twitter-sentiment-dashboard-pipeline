# final-project-twitter
Group Members: Fiona Lee, Yutai Li, Emily Yeh, Helen Yap
## Initial Proposal
Explain why your project idea helps to solve a social science research problem using large-scale computing methods and outline a schedule for completing the project by the deadline. If you are working in a group, you should also write down the names of your group members and describe how you are going to split up the work amongst yourselves. You are welcome to meet with course staff and discuss your ideas with us before submitting your answer to this prompt. 


## Description:
We plan to work on generating a workflow for analyzing the conversation led by opinion leaders on Twitter. We will first stream the Twitter API to the AWS services, and provide analytical data upon keyword queries. By conducting content analysis tasks such as sentiment classification on those tweet conversations and organizing the descriptive information on a dashboard, our pipeline could allow users to gain the insights of how a specified topic is led and discussed by opinion leaders. 

Given the vast growth in social media usage and reliance for news and information, developing a large-scale method to collect and analyze Twitter data as described above would help inform how users feel and perceive the information that can then potentially inform downstream decision-making behaviors.  			

## Schedule Outline:			
Week of 5/9: come up with a clear pipeline and workflow, confirm AWS permissions if applicable  (confirm with one faculty member on Fri. 5/13 or Mon.5/16) <br>
Data Structure: <br>
{“tweet content” :{
	Timestamp: DDMMYYYY, 
	Twitter account (str), 
	Num of comments/retweets (int):,
	Comment sentiment (str):,
	Tweet sentiment (str):,
}
}<br>


Week of 5/16: database/aws instances set up, sentiment analysis model, dashboard, API access; mid-point check in at the end of the week<br>
Week of 5/23: connect all steps together into an automated parallel pipeline<br>
Week of 5/30: Debugging, video presentation recording (includes demo of pipeline)<br>

We will split up the work evenly across all four of us. <br>
Twitter Streaming: Helen Yap<br>
Database Management: Fiona Lee<br>
Sentiment Analysis: Emily Yeh<br>
Dashboard: Yutai Li<br>

