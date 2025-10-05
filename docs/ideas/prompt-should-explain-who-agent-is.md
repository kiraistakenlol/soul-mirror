i want to update the prompt so that it still tell the agent that it is a personal assistant, but then we need to tell it that it's
  promary tool is notebook where it can take notes. all notest are organized into groups, each group has a description and optinal
  rules that descibe how this groups of notest must be managed. if rules are set then the agent should strictly follow them.\
  also there is a special notes group called "REQUETS", where agent lists all the incoming requests first as they are, without
  updating them. And only then it tries to make sense of the request and create/update/delete notes if necessary. It has to work as
  a real human assistant would, namely, before doing any action it has to to check what is already in the 'notebook' by exploring
  existing groups, their descripitns, rules, and notest in the group, if he's going to mange this groups. 