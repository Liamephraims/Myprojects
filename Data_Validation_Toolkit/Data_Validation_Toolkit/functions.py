# import required packages
from pyathena import connect
import pandas as pd
import itertools
import requests
import json
import inspect

# Improvement once completed for all three stages are:

# > All code is now in one file - easier for debugging - also far smaller than previous verison

# > stages are objects - allowing cleaner more intitaive code and inheritance

# > check functions are now wrapped by python decorators, to massage into check objects - easier for non-python native to add own functions, without need for OOP knowledge
# > Need to make sure you add the @check_logic_wrapper wrapper above all check functions

# > Adding in assertions for check functions to declare when wrong input given/customise with meaningful failures messages

# Current issues are:

# > could further simply and neaten code - especially the run_stage_setup methods of stage objects 1, 2 and 3

# Later plan to use on my project AWS/GCP infrastructure for example

#create client class and methods
class client:
    def __init__(self, client, regions, core_databases, zephyr_databases, slack_webhook, connection, send_to_slack=True):
        self.name = client
        self.regions = regions
        self.core_databases = core_databases
        self.zephyr_databases = zephyr_databases
        self.failures = list()
        self.connection = connection
        self.slack_bool = send_to_slack
        self.slack_webhook = slack_webhook
        
    #send data to webhook
    def send_to_slack(self, text):
        WEBHOOK = self.slack_webhook
        data = {"text":text}
        headers = {'content-type': 'application/json'}
        res = requests.post(WEBHOOK, data=json.dumps(data), headers=headers)
        print(res.text)

    # Creating utility function for outputting all the client failures and warnings:
    def output_failures(self):
            """
                Print out the warnings/errors from the validation for client, and if send to slack parameter is not false, then also send to analytics slack channel
            """
            output_string = ""
            # For a particular client:
            output_string += "------------------------------------------------------------Beginning Validation Output for {}-----------------------------------------------------\n".format(self.name)
            output_string += "For client {}, the validation results are:\n".format(self.name)
            for failure in self.failures:
                output_string += failure
            output_string += "------------------------------------------------------------End of Validation Output for {}-----------------------------------------------------\n\n".format(self.name)
            print(output_string)
            if self.slack_bool == True:
                # Then send to slack channel: 
                self.send_to_slack(output_string)
            else:
                print(output_string)
                
class check:
    def __init__(self, function):
        self.name = None
        self.check_function = function
        self.parameters = None
        self.client = None
        self.failure_output = None
    
    # Prepare the check object for running of check function and return output of run:
    def run_logic(self, **check_parameters):   
         
        # intialise uninitalised check parameters
        self.parameters = dict(check_parameters)
        self.name = self.parameters.pop("check_name")
        self.client = self.parameters.pop("client")

        # Get parameters expected for function
        function_parameters = set(inspect.getargspec(self.check_function)[0])

        #Get missed parameters from inputted parameters
        missing_check_parameters = function_parameters.difference(set(self.parameters.keys()))    # Run the logic of check and return its intended output    

        # check that all check parameters have been given that are neccessary for check function
        assert len(missing_check_parameters) == 0, \
                f"For check {self.name} {len(function_parameters)} parameters are missing: {function_parameters} - make sure these are added within the data validation script"     
        
        # Run check by passing through check parameters dictionary
        self.failure_output = self.check_function(**self.parameters)
    
# Creating check function wrapper:

# defining a decorator
def check_logic_wrapper(check_function): 
    """
        A wrapper function for taking a checks function logic, and returning it as a check object
    """
    return check(check_function)
    
########## NOTE: When adding a new check function, make sure to add the check_logic_wrapper above, using syntax @check_logic_wrapper and new check function directly below #######
########## NOTE: Checks should return a tuple containing (1. a true or false bool for whether check condition failed, and 2. the desired print out output for a failure)

# Defining Stage 1 Checks:

# ***** - 1. Define your check function in the desired stage area - ensuring to place it directly underneith the @check_logic_wrapper decorator to wrap it as a check object

@check_logic_wrapper
def check1_1(source, target, sourcedbs, targetdbs, region, uk_connection, regional_connection):
        """ Utility function inheritting from check class, for undertaking check 1.1 for checking the count of regional prod data tables against their aggregated union tables 
        Inputs:
        source - "<table-name>" string e.g.'fact_encounter"
        target - "<table-name>" string e.g.'fact_encounter'
        sourcedbs - "<database-name>" string e.g. 'jj_prod' <- regional prod dbs pushed to uk
        targetdbs - "<database-name>" string e.g. 'jj_prod_union' <- corresponding union dbs in uk
        region - "<region>" string e.g. "ap-southeast-1" (singapore) <- the original region for the prod table before being pushed to uk
        Output:
        bool - True/False - 1/0
        Comments:
        """        
        # Run query of count against the region prod database
        prod_query = """ 
                     SELECT COUNT(*) AS COUNT 
                     FROM {}.{} 
                                """.format(sourcedbs, source)

        prod_query = pd.read_sql(prod_query, regional_connection)
        # Get the count for that regions prod
        region_count = list(prod_query["COUNT"])[0]

        # Run query of count against the region prod database
        union_table_query = """
                                SELECT COUNT(*) AS COUNT  
                                FROM {}.{} 
                                WHERE region = '{}'
                                """.format(targetdbs, target, region)

        union_table_query = pd.read_sql(union_table_query, uk_connection)

        union_count = list(union_table_query["COUNT"])[0]

        print("Check 1.1 (same regional row count): ", union_count== region_count, union_count, target, targetdbs, region_count, source, sourcedbs)

        # Check to see if count is the same for that regional prod table within the union table for that region
        return  union_count== region_count, f"{union_count== region_count} {union_count} {target} {targetdbs} {region_count} {source} {sourcedbs}"

@check_logic_wrapper
def check1_2(target, targetdbs, connection):
        # Run query of count of NULLS against region table
        union_table_query = """
                                SELECT COUNT(*) AS COUNT  
                                FROM {}.{} 
                                WHERE region IS NULL
                                """.format(targetdbs, target)

        union_table_query = pd.read_sql(union_table_query, connection)
        union_count = list(union_table_query["COUNT"])[0]

        print("Check 1.2 (null regions): ", union_count== 0, target, union_count)
        # there should be no nulls in region column for union table
        return  union_count== 0, f" { union_count== 0} {target} {union_count} {target} {targetdbs}"

    
# Defining Stage 2 Checks:
@check_logic_wrapper
def check2_1(target, targetdbs, target_PK, parent_query, prod_ids, connection):
        """ Utility function for undertaking check 2.1, checks that primary key or composite PK key count between union and base tables is the same 
        """
        # for base tables where checking the count of the base table against the prod table does not make sense, will skip this check when requiried. e.g. dim_domain, dim-pathways
        # will return true so does not appear in errors/warnings.
        if parent_query == []:
            print(f"Check 2.1 skipped for {target}--not appropriate")
            return True, f"Check 2.1 skipped for {target}--not appropriate"

        # check if PK is a composite PK so a list, if so need to concat into correct format- otherwise leave as single column string:
        if type(target_PK) == list:
            # then need to concat into string of multiple PK columns:
            target_PK = ','.join(target_PK)

        # check if PK is a composite PK so a list, if so need to concat into correct format- otherwise leave as single column string:
        if type(prod_ids) == list:
            # then need to concat into string of multiple PK columns:
            prod_ids = ','.join(prod_ids)

        # Getting PK count query
        base_query = pd.read_sql("""
                                SELECT COUNT(*) AS COUNT
                                FROM
                                (
                                    SELECT DISTINCT {} 
                                    FROM {}.{} 
                                )
                                """.format(target_PK, targetdbs, target ), connection)
        # actual count for base
        base_count = list(base_query["COUNT"])[0]      

        # Getting parent count athena query
        parent_query = pd.read_sql("""
                                        SELECT COUNT(*) AS COUNT
                                        FROM
                                        (
                                            SELECT DISTINCT {}
                                            {}
                                        )

                                    """.format(prod_ids, parent_query), connection)

        # actual count for union parent table
        parent_count = list(parent_query["COUNT"])[0]     
        #print(union_count,base_count,table)   

        print("Check 2.1 (same PK count): ", parent_count== base_count, target, parent_count, base_count)
        # check result
        return parent_count== base_count, f"{parent_count== base_count} {target} {parent_count} {base_count}"

@check_logic_wrapper
def check2_2(target, targetdbs, target_PK, parent_query, prod_ids, connection):

        """ Utility function for undertaking check 2.2, checks that primary key or composite PK key of base are all in primary key of union table
        """
        # for base tables where checking the count of the base table against the prod table does not make sense, will skip this check when requiried. e.g. dim_domain, dim-pathways
        # will return true so does not appear in errors/warnings.
        if parent_query == []:
            print(f"Check 2.2 skipped for {target}-not appropriate")
            return True, f"Check 2.2 skipped for {target}-not appropriate"

            # check if PK is a composite PK so a list, if so need to concat into correct format- otherwise leave as single column string:
        if type(target_PK) == list:
            # then need to concat into string of multiple PK columns:
            target_PK = ','.join(target_PK)

        # check if PK is a composite PK so a list, if so need to concat into correct format- otherwise leave as single column string:
        if type(prod_ids) == list:
            # then need to concat into string of multiple PK columns:
            prod_ids = ','.join(prod_ids)

        # Getting PK count query
        base_query = pd.read_sql("""
                                SELECT DISTINCT {} AS PK_base  FROM {}.{} 
                                """.format(target_PK, targetdbs, target ), connection)
        # actual count for base
        base_set = set(base_query["PK_base"])   

        # Getting union count query
        parent_query = pd.read_sql("""
                                        SELECT  DISTINCT {} AS union_PK {}
                                    """.format(prod_ids, parent_query), connection)

        # actual count for union source table
        union_set = set(parent_query["union_PK"]) 

        print("Check 2.2 (same distinct PKs): ", (len(union_set.intersection(base_set)) == len(union_set)) and (len(base_set.intersection(union_set)) == len(base_set)), target,  targetdbs )
        # check result: Logic - the intersection between base primary keys and union primary keys are the same - i.e. same primary keys in both base & union
        return (len(union_set.intersection(base_set)) == len(union_set)) and (len(base_set.intersection(union_set)) == len(base_set)), f"{(len(union_set.intersection(base_set)) == len(union_set)) and (len(base_set.intersection(union_set)) == len(base_set))} {target} {targetdbs}"  

######################### Check 2.3 definition - Check that every primary key is unique within base tables ############################################################################

@check_logic_wrapper
def check2_3(target, targetdbs, target_PK, connection):
        """ Utility function for undertaking check 2.3, checks that every primary key is unique - for base tables this is only the primary id and not the update time	
        Inputs:
            target -  string base table name  - e.g. fact_encounter
            targetdbs - string base table database name - e.g. jj_base_tables
            target_PK - the list or string of the primary key columns of table - e.g. encounter_id or if composite (pathway_name, region) as list
                            note: this is derived from the index for the id/column to be counted in base table - col 0 (1) for jj_base_tables.fact_encounter
                                within the input section for each client
        Output:
            bool - True/False - 1/0
        Comments:
        """ 
        # check if PK is a composite PK so a list, if so need to concat into correct format- otherwise leave as single column string:
        if type(target_PK) == list:
            # then need to concat into string of multiple PK columns:
            target_PK = ','.join(target_PK)

        # Getting PK count query
        base_query = pd.read_sql("""
                                    SELECT 
                                        {} AS PK_base, COUNT(*) AS COUNTER 
                                    FROM {}.{} 
                                    GROUP BY {}
                                    HAVING COUNT(*) > 1
                                """.format(target_PK, targetdbs, target, target_PK), connection)

        # check if there are any primary keys within this table - indicating duplicate primary keys - count > 1 so length of column turned to set > 0
        base_set = set(base_query["PK_base"])   
        base_list = list(base_query["PK_base"])
        dup_keys = len(base_set)
        print("Check 2.3 (unique PKs): ",dup_keys ==0, target, dup_keys)

        # return whether this test is true - passed - or false - failed for not containing any duplicate primary keys/primary keys are unique
        return dup_keys ==0, f"{dup_keys ==0} table {target} of database  {targetdbs}  with primary key {target_PK} has {dup_keys} duplicates"

######################### Check 2.4 definition - Check that for a base table which has a column which has an assumption based on a definition, that definition is up-to-date with all definition values - e.g. ecp roles   ############################################################################
@check_logic_wrapper
def check2_4(definition, look_up_database, look_up_table, look_up_column, look_up_inclusion_flag, connection):
            """ Utility function for check 2.4, checking that defintion look-up tables are up-to-date - ie no new values in prod which are not in exclusion set & in look-up table
                    Inputs:
                        look-up definition = a string of the name of the defintion to be displayed on print out - e.g. ecp role definition
                        look_up_database = database name string for look up table - e.g. jj_sandbox
                        look_up_table = table name string for look-up table - e.g. ecp_user_roles_LOOK_UP
                        look_up_column = column name string of look-up table for value set being maintained - e.g. name
                        look_up_inclusion_flag = the column which indicates categorisation of look-up value
                        connection: the athena aws connection object
                    Output:
                        bool - True/False - 1/0
            """ 
            # Getting the definition values for base look-up table:
            base_query = pd.read_sql(f"""
                                        SELECT DISTINCT {look_up_column}
                                        FROM {look_up_database}.{look_up_table}
                                        WHERE {look_up_inclusion_flag} IS NULL -- looking to see if any null look-up values
                                        AND {look_up_column} IS NOT NULL
                                    """, connection)

            # Getting the set of distinct values of base look-up table:
            base_set = set(base_query[look_up_column])

            print("Check 2.4 (no missed/uncategorised look-up values): ", len(base_set)==0, f'- current missing/uncategorised ({definition}) definition values for column ({look_up_column}) in database ({look_up_table}) are:',base_set)

            # Checking that after excluding all definition values that do not fit the definition, that there are no news one which have been missed from the base defintion look-up table
            return len(base_set)==0, f"{len(base_set)==0} - current missing/uncategorised ({definition}) definition values for column ({look_up_column}) in database ({look_up_table}) are: {base_set}"
    
######################### Check 2.5 definition - a warning check function for tracking the number of a particular object - e.g. no. null countries for orgs   ############################################################################
@check_logic_wrapper
def check2_5(tracking_name, tracking_query, expected_result, track_type, connection):
            """ Utility function for check 2.5, a function for tracking a query output on the base tables (though could be from any table/database) (e.g. number of null countries) whereby output should be none.
                    Inputs:
                        tracking_name = a string of the name of the this being tracked for warning print out - e.g. no. orgs with null country
                        tracking_query = the query to get the count of thing being tracked
                        expected_result = integer: what the number of this tracked thing should be - e.g. 0 orgs with null country
                        track_type = whether to compare a count or to show values from query as set
                        connection: the athena aws connection object
                    Output:
                        bool - True/False - 1/0
            """ 
            # run the tracking query - this needs to result in a count, with the final select being named as count
            tracked_output = pd.read_sql(tracking_query ,connection)
            if track_type == 'count':
                # pulling out the count of tracked thing as an integer for comparison
                tracked_output = tracked_output['count'][0]

                # Checking tracked output against the expected output:
                check_bool = tracked_output == expected_result

            if track_type == 'set':
                tracked_output = set(tracked_output['set'])
                check_bool = len(tracked_output) == 0
                expected_result = set()
            print(check_bool, f"Check 2.5: {check_bool} | tracked object: {tracking_name} | tracked no. : {tracked_output} | expected no.: {expected_result} ")
            return check_bool, f"Check 2.5: {check_bool} | tracked object: {tracking_name} | tracked no. : {tracked_output} | expected no.: {expected_result} "
                
# Defining Stage 3 Checks:

#Keeping this as unwrapped function for use in check 3_1:
def check3_1(pathway_set, pathways, dashboard_stat, base_PK_by_pathways, connection):
    """ Utility function for undertaking check 3.2, checks that select all == individual pathway sums"""

    # get the select all total:
    select_all_total = list(pathways[pathways["pathway_name"] == "Select all"]["{}".format(dashboard_stat)])[0]

    # sum variable for capturing aggregated sum of pathways
    pathway_total = 0
    pathway_counts = list()
    pathway_counts.append( (list(pathways[pathways["pathway_name"] == "Select all"]["{}".format(dashboard_stat)])[0],  "Select all") )
    # remove select all from pathway_set, so only non-select all pathways:
    pathway_set.remove("Select all")

    # getting sum of specific pathways (other than select all):
    for pathway in pathway_set:
        pathway_sum = list(pathways[pathways["pathway_name"] == pathway]["{}".format(dashboard_stat)])[0]
        # Incrementing pathway total
        pathway_total = pathway_total + pathway_sum
        pathway_counts.append((pathway_sum, pathway))

    # If for this dash statistic, there is a possibility of a single entity - e.g. patient - being over mutiple pathways and being counted twice
    # then we need to minus from the pathway total (pathways added together - not select all) - we do this by minusing the number of ids shared on a pair of pathways:
    #1. check if there is possiblity of this:
            
    # record no intersections (e.g. same patients on diff pathways) to be minuses from select all at end
    no_intersections = 0
    
    if base_PK_by_pathways != []:
        # then read in base_PK_by_pathways and this is a statstic we need to account for multiple ids between pathways - to avoid being counted twice against select all
        base_PK_by_pathways = pd.read_sql(base_PK_by_pathways,connection)

        # for each pathway get the set of unique base ids
        pathway_dict = dict()
        base_id = base_PK_by_pathways.columns[0] # CONSTRAINT: getting the base id - must be PK id of query given by user
        for pathway in set(base_PK_by_pathways["pathway_name"]):
            pathway_dict[pathway] = set(base_PK_by_pathways[base_PK_by_pathways.pathway_name == pathway][base_id])

        # for each distinct permutation - possible pair of pathways - to see if any same e.g. patient on a pathway (to avoid being counted twice) - check for intersection and add to count 
        pathway_permutations = list(itertools.combinations((set(base_PK_by_pathways["pathway_name"])), 2))
        # for each element i of the list of distinct possible pathway combinations, get the number of intersections (e.g. same patients over two pathways) and sum this number
        no_intersections = sum(list(map(lambda i: len(pathway_dict[i[0]].intersection(pathway_dict[i[1]])) ,  pathway_permutations)))
    
        # now we have number of entities (e.g. patients) which are on multiple pathway pairs we can factor this into our pathway total for comparison against select all
        pathway_total = pathway_total - no_intersections 
    
    # confirming that select all == (all pathway sums added together)
    print('Check 3.1 (select all == pathway sum):', select_all_total == pathway_total, dashboard_stat, select_all_total,  pathway_total)
    
    return select_all_total == pathway_total, f" {select_all_total} == {pathway_total}, {select_all_total},  {pathway_total} {pathway_counts} {dashboard_stat} over multiple pathways accounted for {no_intersections}"

######################### Check 3.2 definition - Check 2 for stage 3 Dashboard checks - checking NON-cumulative & NON-onboard user dashboard statistics & check 3.1  ############################################################################

# in future, should add in method for inference of schema from each script for prod, union, base table, end-point tables
# and matching of primary keys together
@check_logic_wrapper
def check3_2(dashboard_statistic, base_statistic_query, dash_table, dash_database, base_PK_by_pathways, connection):
            """ Utility function for undertaking check 3.2, checks that a dashboard statistic in end-point dashboard table has the same sum as when calculated 
            directly off the relevant base tables and checks that check 3.1 is true"""
            # Calculating the sum for the dashboard statistic
            dash_statistic_query = """
                                            SELECT SUM({}) 
                                            FROM {}.{}
                                        """.format(dashboard_statistic,dash_database,dash_table)

            #  getting all pathways for this dashboard statistic:
            # creating defaiult bool for check1
            check3_1 = True, f""

            # checking if pathway_name column:
            pathway_check = pd.read_sql(
            """
                SELECT *
                FROM {}.{} 
            """.format(dash_database, dash_table) ,connection).columns

            if "pathway_name" in set(pathway_check):

                pathways = pd.read_sql("""
                    SELECT 
                        pathway_name, SUM({}) as {} 
                    FROM {}.{} 
                    GROUP BY pathway_name
                """.format(dashboard_statistic, dashboard_statistic, dash_database, dash_table) ,connection)

                # getting all distinct pathway name values
                pathway_set = set(pathways["pathway_name"])

                # setting a default boolean for check 3.1 (that a select all == sum of individual pathways if multiple pathways) with default true - in case not multiple pathways 

                # checking if there is a select all (ie. multiple pathways):
                if "Select all" in pathway_set:
                    # then will need to compare select all against overall base table statistic - because sum over dashboard statistic would be wrong for check 3.1
                    dash_statistic_query = dash_statistic_query + " WHERE pathway_name = 'Select all'"

                    # furthermore, knowing that this is a multiple pathway, need to check that the pathways underlying the select all are also correct, so completeing a nested check for this
                    check3_1 = check_3_1(pathway_set, pathways, dashboard_statistic, base_PK_by_pathways,connection) 

            dash_statistic = pd.read_sql(dash_statistic_query, connection)
            dash_statistic = list(dash_statistic["_col0"])[0]

            # Calculating the sum for base table query for the same statistic
            base_statistic = pd.read_sql(base_statistic_query, connection)
            base_statistic = list(base_statistic["_col0"])[0]

            # check logic: both sums are equal
            print("Check 3.2 (base to dash same sum): ", base_statistic==dash_statistic, base_statistic,dash_statistic, dash_table, dashboard_statistic)

            # check that the base statistic query is equal to the sumed base dashboard statistic (check 3.2) 
            #    AND if is a multiple pathway that select all == sum of individual pathways in dashboard table alone (check 3.1)
            return (base_statistic==dash_statistic) and (check3_1[0] == True), f" check3_1: {check3_1[0]} {check3_1[1]} | check3_2:  {base_statistic==dash_statistic} {base_statistic,dash_statistic} {dash_table} {dashboard_statistic} "
    
    ######################### Check 3.3 definition - Check 3 for stage 3 Dashboard checks - checking cumulative  statistics   ############################################################################
@check_logic_wrapper
def check3_3(cumulative_dash_query, base_dash_query, cumulative_dash_statistic, connection):
            """ Utility function to test that for the cumulative table, if select all than this is equal the overall base statistic total - query should be by country summed   """
            # read in the cumulative data table from athena for all regions
            cumulative_dash_query = pd.read_sql(cumulative_dash_query, connection)

            # read in the base data table from athena for the overall count of the dash statistic over all regions
            base_dash_read = pd.read_sql(base_dash_query, connection)

            # checking by country cumulative sum is equal to base stat
            cum_sum = cumulative_dash_query['count'][0]
            base_cnt = base_dash_read['count'][0]

            # checking result var
            check_bool = bool(cum_sum == base_cnt)

            # completing check for 3.3, if any failures in pathway+region cumulative totals not adding up  or the overall select all not adding up to base query then inconsistency in cumualtive:
            print("Check 3.3 (select all == cumulative total): ", check_bool == 1,base_cnt, cum_sum, cumulative_dash_statistic)

            return  check_bool, f"{check_bool == 1} {base_cnt} {cum_sum} {cumulative_dash_statistic}"
    
    ######################### Check 3.4 definition - Check 3 for stage 3 Dashboard checks - checking onboard (single-level pathway)  statistics  -where sum would not work over multiple pathways ############################################################################
@check_logic_wrapper
def check3_4(dashboard_statistic, dash_database, dash_table, base_statistic_query, connection):
            """ Utility function to test check 3.4, which computes if a dashboard statistic, which cannot be summed across pathways as same for all - e.g. onboarded users is the same as base    """
            #  getting all pathways for  dashboard statistic:
            pathways = pd.read_sql("""
                SELECT 
                    pathway_name, SUM({}) as {} 
                FROM {}.{} 
                GROUP BY pathway_name
            """.format(dashboard_statistic, dashboard_statistic, dash_database, dash_table) ,connection)

            # getting all distinct pathway name values
            pathway_set = set(pathways["pathway_name"])


            pathway_sum_list = list()
            # for all pathways add the sum to a list, then sum this list, then divide by number of pathways - this should end up at the same number if all are equal as they are supposed to be
            for pathway in pathway_set:
                path_total = list(pathways[pathways["pathway_name"] == pathway]["{}".format(dashboard_statistic)])[0]
                pathway_sum_list.append(path_total)
            # now summing that list for sum across all pathways (including select all if present)
            pathway_total_sum = sum(pathway_sum_list)
            # no. of pathways
            no_pathways = len(pathway_set)
            # default bool for updating if a false level comparison with base statistic:
            pathway_bool = True

            # now getting the base query total to make sure this is also the same 
            base_statistic = pd.read_sql(base_statistic_query, connection)
            base_statistic = list(base_statistic["_col0"])[0]

            # list for recording the counts of each level for later printing
            random_pathway_counts = list()

            # for each pathway, pop and make sure is same sum as the base: break if either there is a false or empty stack:
            while len(pathway_set) > 0 and pathway_bool != False:
                # taking a pathway name from the set and getting the count to compare against base statistic
                popped_pathway = pathway_set.pop()
                random_pathway_count = list(pathways[pathways["pathway_name"] == popped_pathway]["{}".format(dashboard_statistic)])[0]
                # add count to list for later printing in check output
                random_pathway_counts.append((popped_pathway, random_pathway_count))
                # comparing against base statistic and updating the pathway_bool (if false then will update otherwise will remain true)
                pathway_bool = (random_pathway_count == base_statistic)

            # bool for checking if all pathways are equal value across pathways, including select all and equal to the base statistic
            paths_equal_bool = pathway_total_sum / no_pathways == base_statistic

            print("Check 3.4 (onboard stat dash->base same): ", (base_statistic == random_pathway_count and paths_equal_bool == True), dashboard_statistic)

            # Now having confirmed that all pathway counts are the same for this statistic, making sure that one of them is equal to the base table query for this statistic
            return pathway_bool == True and paths_equal_bool == True, f"{pathway_bool == True and paths_equal_bool == True} {dashboard_statistic} {random_pathway_counts} {base_statistic} {pathway_total_sum / no_pathways}"
        
    ######################### Check 3.5 definition - Check 3 for stage 3 Dashboard checks - checking onboard (single-level pathway)  statistics  -where sum would not work over multiple pathways ############################################################################
@check_logic_wrapper
def check3_5(business_logic_query, base_stat_query, business_logic_name, connection):
            """     General utility function to compare if two queries are the same, generalised for testing business logic queries against base table queries  or could also check between dashboard queries   
                   NOTE: Needs to be queries resulting in single counts/ count comparison  """
            # running the result for business logic
            business_logic_query = pd.read_sql(business_logic_query, connection)
            business_logic_query_result = list(business_logic_query["_col0"])[0]

            # running the result for base query comparison
            base_stat_query = pd.read_sql(base_stat_query, connection)
            base_stat_query_result = list(base_stat_query["_col0"])[0]

            # outputting result of comparison
            print(f"Check 3.5 (business logic-{business_logic_name}): ", (base_stat_query_result == business_logic_query_result), base_stat_query_result, business_logic_query_result)

            # returning whether business logic check was passed:
            return base_stat_query_result == business_logic_query_result, f"business logic-{business_logic_name}: {base_stat_query_result == business_logic_query_result} {base_stat_query_result} {business_logic_query_result}"
        
    ######################### Check 3.6 definition - essentially same as above - Check 3 for stage 3 Dashboard checks - Checking between dashboard figures or business logic totals within the dashboard
@check_logic_wrapper
def check3_6(dash_query_1, dash_query_2, dash_test_name, logical_comparion_operator, connection):
            """     General utility function to compare if two queries are the same, used in this case for two generic dashboard figures or queries  """
            # running the result for dash query 1 comparison
            dash_query_1 = pd.read_sql(dash_query_1, connection)
            #print(dash_query_1)
            dash1_query_result = list(dash_query_1["_col0"])[0]

            # running the result for dash query 2 comparison
            dash_query_2 = pd.read_sql(dash_query_2, connection)
            #print(dash_query_2)
            dash2_query_result = list(dash_query_2["_col0"])[0]

            # outputting result of comparison
            print(f"Check 3.6 (within-dash check-{dash_test_name}): ", eval("{} {} {}".format(dash1_query_result, logical_comparion_operator,dash2_query_result)), dash2_query_result, dash1_query_result)
            # returning whether dash comparison check was passed: NOTE: this will evaluate the string as a logical expression - allowing for the logic operator to be dynamic
            output = eval("{} {} {}".format(dash1_query_result, logical_comparion_operator,dash2_query_result))
            return eval("{} {} {}".format(dash1_query_result, logical_comparion_operator,dash2_query_result)), f"{output} {dash1_query_result} {logical_comparion_operator} {dash2_query_result}"        
    

# Stages set-up

# Define child driver for stage 1
class stage_1:
    def __init__(self,name, client, check_set, **kwargs):
        # This will intialise a stage_1 object, and use the parameters to give this object instance its attributes - and to other stage classes (2 and 3)
        self.name = name
        self.client = client
        self.check_set = check_set
        self.stage_setup_outputs = list()
        self.regional_connectors = dict()
        # CUSTOM PARAMETER LISTS for holding custom parameters later on when running in prep_stage_check_parameters - 

        # ***** - 5. Add the new check below, to initalise a list for it when passing through the custom parameters provided in the data validation script
##################################################################################################### ADD ANY NEW CHECK HERE AS check_name: list() ######################################################################################
        # Defines lists for each check, where custom check parameters will be stored
        self.check_custom_parameters = { # Stage 1 checks
                                       "1.1": list() , "1.2":list(), 
                                        # Stage 2 checks
                                       "2.1":list(), "2.2":list(), "2.3":list(), "2.4":list(), "2.5":list(),
                                       # Stage 3 checks
                                       "3.2":list(), "3.3":list(), "3.4":list(), "3.5":list(), "3.6":list()
                                      }
################################################################################################### INCLUDE MANDATORY AND OPTIONAL DEFAULT PARAMETERS HERE ##################################################################
        # MANDATORY DEFAULT PARAMETERS (Check_object, check_name, client
        # OPTIONAL DEFAULT PARAMETERS - e.g. client name + dashboard_tables, athena connection object (though likely needed for any check running athena commands) - both being check specific
        # A dictionary containing the default parameters for each check:
        # ***** - 6. Add the default parameters required in your check, including any optional ones you can include here rather than having to include as a parameter provided by the user.
        #            Mandatory default parameters are provided as a dictionary with the name of your check, and key-value parameters are;
        #                   i.   check_object: the check class object
        #                   ii.  check_name: the name of the check again ( this really should just come from the name of the dictionary key - an example of some weaknesses in code structure )
        #                   iii. client: the name of the client, provided from the client object in the stage.client attribute
        self.check_default_parameters = {
           "1.1": { "check_object": check1_1, "check_name" : '1.1', "client" : self.client, "targetdbs" : self.client.name + "_prod_union", "uk_connection" : self.client.connection}, 
           "1.2": { "check_object": check1_2, "check_name" : '1.2', "client" : self.client, "targetdbs" : self.client.name + "_prod_union","connection" : self.client.connection}, 
           "2.1": {"check_object":  check2_1, "check_name" : '2.1', "client" :  self.client, "connection" : self.client.connection}, 
           "2.2": {"check_object":  check2_2, "check_name" : '2.2', "client" : self.client, "connection" :self.client.connection}, 
           "2.3": {"check_object":  check2_3, "check_name" : '2.3', "client" : self.client, "connection" :self.client.connection}, 
           "2.4": {"check_object":  check2_4, "check_name" : '2.4', "client" : self.client, "connection" :self.client.connection}, 
           "2.5": {"check_object":  check2_5, "check_name" : '2.5', "client" : self.client, "connection" :self.client.connection},
           "3.2": {"check_object":  check3_2, "check_name" : '3.2', "client" : self.client, "connection" :self.client.connection, "dash_database" : self.client.name + "_dashboard_tables"}, 
           "3.3": {"check_object":  check3_3, "check_name" : '3.3', "client" : self.client, "connection" :self.client.connection}, 
           "3.4": {"check_object":  check3_4, "check_name" : '3.4', "client" : self.client, "connection" :self.client.connection, "dash_database" : self.client.name + "_dashboard_tables"}, 
           "3.5": {"check_object":  check3_5, "check_name" : '3.5', "client" : self.client, "connection" :self.client.connection}, 
           "3.6": {"check_object":  check3_6, "check_name" : '3.6', "client" : self.client, "connection" :self.client.connection}
                                         }   
        # stores the passed dictionaries from the data validation template for that stage, storing these in a dictionary for use in run_stage_setup for unnesting to level of individual parameter dictionaries 
        self.kwarg_parameters = dict(kwargs) 
        
    #Unnest all stage inputs into final set-up variables:    
    def run_stage_setup(self):
        # note each setup is a manual step, due to stage specific manipulations of input dictionaries from validation template
        # Checks being undertaken:
        #      1.1 - Check that for a prod region, there is same amount of rows for that region in union table
        #      1.2 - Check that for union table there is no null values
        # 5 a. Obtain all possible union tables from all regions of client:
        tables = dict()
        stage_1_parameters = list()
        for index in range(0, len(self.client.regions)): 
            core_database = self.client.core_databases[index]
            zephyr_database = self.client.zephyr_databases[index] 
            region = self.client.regions[index]
            union_query = f"""
                            SELECT TABLE_NAME
                            FROM information_schema.TABLES
                            WHERE table_schema = '{self.client.name + "_prod_union"}'  """
            union_tables = set(pd.read_sql(union_query , self.client.connection)["TABLE_NAME"])
            regional_connection = connect(s3_staging_dir=f's3://aws-athena-query-results-{region}-819482042493/',
                   region_name= f'{region}')
            self.regional_connectors[region] = regional_connection
            tables_query = f"""
                            SELECT TABLE_NAME, table_schema  
                            FROM information_schema.TABLES
                            WHERE table_schema IN ('{zephyr_database}', '{core_database}')
                            AND NOT TABLE_NAME LIKE '%information_schema%' """
            tabledf = pd.read_sql(tables_query , regional_connection)
            # Saving the core tables
            core_region_tables = set(tabledf[(tabledf.table_schema == f"{core_database}")]["TABLE_NAME"])
            tables[(region, core_database)] = core_region_tables
            # Saving the zephyr tables
            zephyr_region_tables = set(tabledf[(tabledf.table_schema == f"{zephyr_database}")]["TABLE_NAME"])
            tables[(region, zephyr_database)] = zephyr_region_tables
            # unnesting for parameter level:
            for region,prod_database in tables:
                for table in tables[(region, prod_database)]:
                    if table in union_tables:
                        stage_1_parameters.append({"source" : table,"target" : table, "sourcedbs" :prod_database,
                                                                "region" :region, "regional_connection" :self.regional_connectors[region]})
        # This is the important step for adding any new check dictionaries into validation
        # format needs to be in a single dictionary, containing the intended name of the check to use on the list object of parameter inputs from data val script
        # note: any setup objects, need to result in a setup object which is a list of dictionaries with each dictionary item consisting of the key-values of a checks CUSTOM parameters - though flexibility in getting tp final object below

        # # Store set-up custom check parameter object for 1.1 and 1.2: indicating one for each check even if uses same object - could be improved
        self.stage_setup_outputs.append(["1.1",stage_1_parameters]) 
        self.stage_setup_outputs.append(["1.2",stage_1_parameters]) 
        
    # Collect all parameters for each check:
    def prep_stage_check_parameters(self):
        
        # Iterate over all stored customer parameter objects in the stage_setup_outputs list
        for check_object_list in self.stage_setup_outputs:
                # Using the objects pull out the name of the check and the dictionary of input parameters
                check_name = check_object_list[0] 
                check_parameter_list = check_object_list[1]
                
                # Confirm that the check exists in both the default checks, and also in has a list in the check_custom_parameters for saving each parameter row 
                assert check_name in self.check_custom_parameters, f" Check {check_name} is missing from stage class check_custom_parameters dictionary add check if you want it to be run in stage {self.name}"
                assert check_name in self.check_default_parameters, f" Check {check_name} is missing from stage class check_default_parameters dictionary, please add check if you want it to be run in stage {self.name}"        
                
                # Save the default parameters for the check:
                default_parameters=self.check_default_parameters[check_name]
                
                # Pulling out individual check as a list containing all the custom parameters (not default) parameters needed to run a single check instance :
                for custom_parameter_row in check_parameter_list:
                    
                    # merge default parameters with custom parameters key-values pairs:
                    check_parameters = {**custom_parameter_row,**default_parameters}
                    
                    # Use the dictionary check key to add the key-value parameter values for a check instance/row
                    self.check_custom_parameters[check_name].append(check_parameters)        
   
    # Run all generic checks for stage and manage failures (this will be defined once, and inherited by all other stages):
    # Note: this function will be used/inherited in all subsequent stage drivers
    def run_stage_checks(self):
            
            # Run the set-up for the stage, transforming all inputs into unnested step outputs 
            self.run_stage_setup()
            
            # Using setup outputs, create the parameters and checks to be run for this stage, fully unnested to run check by row:
            self.prep_stage_check_parameters()
            
            # Using stage check parameters run all checks:
            for check_name in self.check_custom_parameters:
                # get each instance of check parameters for a single check
                for check_instance in self.check_custom_parameters[check_name]:
                    
                    # Make sure this is a check user wants to be run:
                    if (check_name in self.check_set):
                        
                        #if so intialise the check:
                        check_object = check_instance.pop("check_object")
                        assert check_object != None, f"Check Object was not added to Check {check_name} in method prep_stage_check_parameters for Stage {self.name}"
                        
                        # Run check by passing check parameters and save output to check.failure_output attribute
                        check_object.run_logic(**check_instance)  
                        
                        # save failure output for later printing if failed check
                        if check_object.failure_output[0] == 0:
                            self.client.failures.append(check_object.failure_output[1])
            print(f"Finished {self.name} checks for {self.client.name}")
            
            # Returns the client object after having run the latest stage - giving latest failures
            return self.client
        
        
# Define child driver for stage 1
class stage_2(stage_1):
    
    # Inherits  def run_stage_checks(self) and def __init__(self, name, client, check_set) from Stage_1 parent class
    def run_stage_setup(self):
        # ***** - 7. Depending on the stage you want to add the check to (for example adding to stage 2), then you will add the input list object as a parameter below in the stage_parameters
        # Firstly, check that all neccessary parameters have been inputted:
        stage_parameters = {"source_target_input_list", "definition_check_list", "track_check_list"}
        assert(all(x in stage_parameters for x in self.kwarg_parameters.keys()),
                        f"For stage {self.name} one of set-up parameters is missing: {stage_parameters} - note all parameters need to be keyword parameters")
        # ***** - 8. You will then need to create the variable with same name below (note this could be removed and self.kwarg_parameters["list object name"]) could be used instead - optional to remove this step
        # Collecting stage 2 set-up custom parameter dictionaries:
        source_target_input_list = self.kwarg_parameters["source_target_input_list"]
        definition_check_list = self.kwarg_parameters["definition_check_list"]
        track_check_list = self.kwarg_parameters["track_check_list"]
        
        # Store set-up custom check parameter object for 2.1, 2.2, 2.3
        self.stage_setup_outputs.append(["2.1",source_target_input_list]) 
        self.stage_setup_outputs.append(["2.2", source_target_input_list]) 
        self.stage_setup_outputs.append(["2.2", source_target_input_list])         
        
        # Store set-up custom check parameter object for 2.4
        self.stage_setup_outputs.append(["2.4", definition_check_list])        
        
        # Store set-up custom check parameter object for 2.5:
        self.stage_setup_outputs.append(["2.5", track_check_list]) 
# ***** - 9. Finally, you will need to create some unnesting code (if not at level of list with dictionaries of key-value parameters appended), and then add this to the self.stage_setup_outputs attribute so the prep_check_parameters function can access them

##################################################################### ADD ANY FUTURE CHECKS INPUT LISTS BELOW FOR STAGE 2 ###############################################
# note: You will need to ensure these are extracted to the level of a list, containing a dictionary of key-value parameters for the check - each dictionary being one instance of a check to be run
# There is flexiblity here for the input to be anything, as long as the end output is a list. Which can then be appended to the stage_setup_objects attribute with the check name provided (and check added in stage 1)

        
# # Define stage 3 class object, inheriting from stage_2 as most similar
class stage_3(stage_2):
    # Inherits  def run_stage_checks(self) and def __init__(self, name, client, check_set) from Stage_2 parent class
    def run_stage_setup(self):
        # Firstly, check that all parameters have been inputted:
        stage_parameters = {"dash_to_base_query_list", "cumulative_check_list", "onboard_stat_list", "business_logic_list", "between_dash_comparison_list"}
        assert(all(x in stage_parameters for x in self.kwarg_parameters.keys()),
                        f"For stage {self.name} one of set-up parameters is missing: {stage_parameters} - note all parameters need to be keyword parameters")
        
        # Collecting stage 2 set-up parameters:
        dash_to_base_query_list = self.kwarg_parameters["dash_to_base_query_list"]
        cumulative_check_list = self.kwarg_parameters["cumulative_check_list"]
        onboard_stat_list = self.kwarg_parameters["onboard_stat_list"]
        business_logic_list = self.kwarg_parameters["business_logic_list"]
        between_dash_comparison_list = self.kwarg_parameters["between_dash_comparison_list"]
        
        # Store set-up custom check parameter object for 3.2
        self.stage_setup_outputs.append(["3.2", dash_to_base_query_list]) 
        # Store set-up custom check parameter object for 3.3
        self.stage_setup_outputs.append(["3.3", cumulative_check_list])         
        # Store set-up custom check parameter object for 3.4
        self.stage_setup_outputs.append(["3.4", onboard_stat_list])        
        # Store set-up custom check parameter object for 3.5:
        self.stage_setup_outputs.append(["3.5", business_logic_list])  
        # Store set-up custom check parameter object for 3.6:
        self.stage_setup_outputs.append(["3.6", between_dash_comparison_list])   
##################################################################### ADD ANY FUTURE CHECKS INPUT LISTS BELOW FOR STAGE 2 ###############################################
# note: You will need to ensure these are extracted to the level of a list, containing a dictionary of key-value parameters for the check - each dictionary being one instance of a check to be run
# There is flexiblity here for the input to be anything, as long as the end output is a list. Which can then be appended to the stage_setup_objects attribute with the check name provided (and check added in stage 1)
        
