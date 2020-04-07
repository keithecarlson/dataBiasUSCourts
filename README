This file contains detailed step-by-step instructions to reproduce all results of our experiment.  All provided code files should be run from within the "Code" directory.

1. First we will setup the environments to be sure we have the correct versions of various libraries installed and that they don't change during our full run of the analysis.  Setup a packrat R environment (http://rstudio.github.io/packrat/walkthrough.html) in the Code directory of your project.  We use packrat version 0.5.0.  You can attempt to use our bundled version of the packrat project, but we have not tested this on other systems so it is possible you will encounter issues.  To try this, download 'dataBiasCode.tar.gz'.  Create a directory for the project and then within that directory run R.  In R you will enter the command:

	packrat::unbundle("dataBiasCode.tar.gz",".")

Then quit().  You should now have a populated 'Code' directory, complete with the virtual environment for python and the packrat files for R.  If this works, you will be able to skip to step 3 except for needing to activate the virtual environment by navigating to the Code Directory and running:

	source pubBiasVE/bin/activate 

If you are setting up your own packrat project, run R from within your code directory you should see "Packrat mode on. Using library in directory:"

In R, we will now install the libraries we need for the project with:

	install.packages("stm")
	install.packages("tm")
	install.packages("SnowballC") 


2. Setup a python 2.7 virtual environment to control the versions of all python libraries used.  We place this in the Code directory with the following command which you may have to modify to point to your own python 2.7 installation: 	
	
	virtualenv --python=/usr/bin/python2.7 pubBiasVE

When we run any python code we want to be sure it is run from within this virtual environment.  We can activate the environment from within our Code directory with:

	source pubBiasVE/bin/activate

and can deactivate it with:

	deactivate

We can install needed libraries by activating the environment and using pip.  For example:
	
	pip install pandas
	pip install matplotlib
	pip install unidecode
	pip install scipy
	pip install statsmodels

3. If you wish to process the data that we received from the source then follow Dataset Reconstruction Instructions, to create 12 ca{X}DataForSTM.csv files within "Data/stmCSV".  This will also create Results/pruningStats and results/validationSample folders. 

Alternatively, you can skip this step and simply use our already [pruned and processed data](https://math.dartmouth.edu/~jelsdatabiasuscourts/dataset/Data.tar.gz) that is provided.  Either way, you should have a Data/stmCSV folder with 12 files in it, a Data/judges folder with a single file titled 'auburnDataAppointingPresParty.csv', and a file 'Data/uscaopsData01.csv' before you proceed.

4. We will make the plot showing publication rate from 1997-2016 which is in the paper.  Make sure that the file uscaopsData01.csv exists in the Data directory then run:

	python publicationPlot.py

This will create Results/Figures/figure2.png

5. You are now ready to run summaryStats.py:

	python summaryStats.py

This will create summary info about the corpus in the "Results/summaryStats" directory.  The files are USPartyCount.csv and corpPartyCount.csv and these results are reported in Table 2 of the paper.

6. Next run the analysis of the observed panel compositions:

	python expectedPanelComps.py

This will create a file Results/panelBiasResults/panelCompositionResults.txt, with a lot of information about the expected and observed panel compositions, but the major parts reported in the paper (Table 3 and paragraph below it) are at the bottom of the file.

7. Now we will do a similar analysis of judges, to see if the parties of the two other judges on their panels appear to be unbiased.  Run:

	python judgeBias.py

This will create two files in Results/panelBiasResults.  judgeBiasSummary.txt will report the number of judges on each circuit and across the whole corpus who's panel associates reflected bias.  judgeBiases.csv has a line for each judge, reporting the observed associates and expected associates summed across the their career as well as the p-val of the chisquare test.

8. Now we will start using R to create the topic models.  We will first clean and process the data.  Run the following from within the Code directory:

	R -f preProcessData.R

This will create preparedData.Rdata in newly created directory "Data/RData" which is a workspace imamge with all R objects created by the processing.  This includes the vocab, documents and meta information we will use to fit the topic models.  It will also create a file "Results/vocabSize.txt" which tells us the number of unique words in our data after lowercasing, stemming, etc.

9. Next we fit the large 50 topic model. Run:

	R -f fullModelRun.R

This may take a long time (days or longer), but will fit a 50 topic STM on all of our documents.  It will save the model to Data/RData and will output the top words associated with each topic to Results/topicModelWords.  At this point you should look at the words associated with each topic and name them for future use in creation of figures,etc.  For each topic 1-50, one topic per line, write out the label you would like to assign to a file "Results/topicLabels.txt". For example, the first line in our file reads "Procedure (1) court, district, jurisdict, case". These labels appear are used when discussing topics in the paper and for some figures/tables.  We have included the topic labels file that we used in this project.

10.  Now we will fit another 50 topic model on the full dataset, but after permuting the documents' DMP assignments.

	R -f permModelRun.R

This will again take a while, but will produce "Data/RData/50TopicPermDMP.Rdata" holding the fully fit topic model with permuted DMP tags.

11. To slightly simplify some future commands for some regressions, etc, run:

	python createSingleDataFile.py

This will Create Data/lustrumDemCountDataAllCircuits.csv which contains a row for each document and columns for all relevant variables for regressions.


12. We'll run a regression to see the effect of majorityParty on each topic's prevalence with controls for circuit and year.
	
	R -f topicPrevAnalysis.R

This will create files in the newly created Results/topicRegressionResults folder.  One with the information from the regression, and one with the corpus wide average prevalence of each topic.  We'll use these later to produce figure 5.  It will also run the same regression using the permuted 50 topic model and create a file with that information.  This will be compared to the true data regression later.


13. Next we will run our version of the permutation test as described.  Run:

	R -f permTest.R

This will produce a file Results/STMPermutationTest/permTestResults.csv with information on the effect size of DMP on topic prevalence for the topic in which the effect size is largest for each run for both the true and permuted DMP.  This code may also take many days to run because of the large number of topic models being fit.  We attempted to set seeds in a way that this would give identical results if our process is run again, but in 2 different runs of this we ended up with slightly different results.  Therefore, your results from this and step 14 should be roughly the same as we report in the paper, but you may find minor differences.

14. Analyze the results of the permutation test.  
	
	python analyzePermTest.py

This will create a file Results/STMPermutationTest/permTestAnalysis.txt with the average and standard deviation of the largest effect size of DMP on topic prevalence for the true data runs and the permuted data runs.  It will also run several KS and T-Tests showing that these are drawn from different distributions indicating the the DMP must have some effect. 

15. We will do some analysis of the relation between the DMP and USParty variables in our data.  Run:

	python deviationSim.py

This will permute USParty within circuit-years as described in the paper.  It will write the result of a ks test between the the absolute value of 'excess' in all true data circ years vs all permutations of all circ-years to Results/USPartyDMPExcessKSTest.txt.  Additionally it will create Results/Figures/figure3.png which is included in the paper and shows the true excess for all testedYears.

16. Now let's look at the effect of demCount on USParty year by year.  Run:

	python USPartyWindowLogits.py

This runs a regression predicting USParty from demCount and circuit indicators for each year using data from it and the preceding and following year.  It will create a file, Results/USPartyWindowLogitResults.txt with a summary of each model in which the p-value for demcount is <.1 and show the combined p-value of all years at the bottom. It will also create Results/Figures/figure4.png which shows the estimated effect over time as well as a smoothed version of this and of the upper and lower 95% confidence intervals.  

17. To create the figure showing the  effect of DMP on topic prevalence from the regression run:
	
	python topicOLSPlotter.py

This will create and save the figure in Results/Figures/figure5.png

18.  We will now compare the results from the regressions predicting topic prevalence from majorityParty, year, and circuit for the true data and permuted data 50 topic models.

	python averageEffectSize.py

This will create Results/topicRegressionResults/effectSizeKSTest.txt which tells us the average effect size and standard deviation for the 10 biggest effects in each model.  It also performs a KS test to see if they could have been drawn from the same distribution.

19. Find the average prevalence of the top 5 topics in a document:
	
	R -f findAverageTopicPrev.R

This will create a file Results/50TopicTrueDataaverageTopicDensity.txt

20. Tables 4 and 5 are based on a series of logistic regressions run in Stata. The file "lustrumDemCountDataAllCircuits.csv" was created by createSingleDataFile.py and used as the data input for the State do-file "USasparty.do" which runs the regressions that were used to generate the estimates reported in Tables 4 and 5.
