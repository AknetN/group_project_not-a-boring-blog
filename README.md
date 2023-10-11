# group_project_not-a-boring-blog
Group project on blog post website creation

# Work procedure
___
## <u>Configuration</u>
- Git glone project on your machine
- create and activate virtual environment 

==> python3 -m venv <name of virtual environment>

==> source <name of virtual environment>/bin/activate 
- pip install -r requirements.txt
- create a postgresql database (you will need the name of it in the environmental variables, as well your postgres credentials)
- create .env file with the following environmental variables:

> export NAME=""
> 
> export USER=""
> 
> export PASSWORD=""
> 
> export HOST="localhost"
> 
> export PORT="5432"
> 
> export SECRET_KEY=""

- activate your environmental variables by running source .env 

## <u>When starting a new task:</u>

#### <i>Step 1 - check your branch, make sure you always start your task from the last version of main:</i>
> :$ git branch

The prompt should say that you are on main branch.

#### <i>Step 2 - pull from remote repo to make sure you have the latest version of main to avoid conflicts:</i>

> :$ git pull origin main

This will either tell you that you are up to date or it will bring your local branch up to date:

#### <i>Step 3 - create your working branch:</i>

> :$ git checkout -b <name_of_your_branch>

#### <i>Step 4 - make sure you are an your working branch:</i>

> :$ git branch

You should see a prompt with all branches, the current branch(your case should be the branch you just created) will be marked with an asterisk 

> :$ git branch
> 
> main 
> 
> '*' <your_current_branch>

#### <i>Step 5 - Do your thing! Just do it!:</i>
Depending on what you work you should create new files in the according directory.

Working on a model, in the model file create a new .py file with the title of the model or class that is meant for.

For example for a post we will create in /models a new .py file called post.py (don't forget to register the models in the admin file)

#### <i>Step 6 - When you are done stage and commit your work:</i>

User :$ git status to check all files that need to be staged then add the ones you worked on with:

> :$ git add <name_of_file>

or 

> :$ git add .

to add all files, make sure you don't stage any unwanted files, to unstage files use:

> :$ git reset <name_of_file>

Check with git status to see what files are staged, staged files are marked with green.

Finally commit using a descriptive message:

> :$ git commit -m 'created a model for post'

#### <i>Step 7 - push modifications to the remote repository:</i>

Since you are working on your branch when you push you should use the name of your branch

> :$ git push origin <your_current_branch>

With this final step you are done! Ask for someone to review and merge the branches or if there is still a task that is unrelated and can be done without what you just worked one, go back to the main branch

> :$ git checkout main

Now you can start your next task by following all the steps again!

#### <i> Step 8 - additional - delete former work branch:</i>

> :$ git branch -d <your_former_working_branch>

!!! Make sure you do not delete your main branch!!!


___
## Project Description

### <u>Main Features</u>

1. User Management
- New users must be able to register themselves in the system.
- Users need to log in to access the system
- Users must be able to reset their password.

2. Blog Front Page
- A user must be able to have an initial page listing his Blog articles with a preivew of the article
- By clicking the user is redirected to the blog articles
- The initial page must have a menu, with article organized as categories/tags.

3. Articles Management
- A user must be able to create and edit his own blog articles
- A user must be able to select wich articles must appear in the initial page and be public available
- Articles can be in three diferent states, "published", "private", "editing"
- Only published articles can appear in the blog

3. Article sharing
- A user must be able to request permission to publish someonelses article
- If user gets an authorization, the article can be listed in the front page of the blog
- When clicking on details the visitor is redirected to the original authors blog and article.

### <u>Additional Features</u>
1. Comments
- A visitor must be able to comment on articles.
- Comments can have comments.
# group_project_not-a-boring-blog
Group project on blog post website creation
