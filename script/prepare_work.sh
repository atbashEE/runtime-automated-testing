#!/bin/bash
rm prepare_work.log

source config.sh

echo "Creating working directory : $WORKING_DIR and create Python Virtual Environment"
python3 -m venv $WORKING_DIR/venv

Echo "Copy all needed files into working directory"

cp -a $TESTING_HOME/ext/. $WORKING_DIR/

cp -a $TESTING_HOME/python/. $WORKING_DIR/

cp -a $RUNTIME_ZIP $WORKING_DIR/
unzip $WORKING_DIR/atbash-runtime.zip -d $WORKING_DIR/atbash-runtime >> prepare_work.log

cp -a $RUNTIME_CLI_JAR $WORKING_DIR/

cp -a $DEMO_REST_WAR $WORKING_DIR/

cp -a $TESTING_HOME/java/AtbashJFRDump/target/AtbashJFRDump.jar $WORKING_DIR/
cp -a $TESTING_HOME/java/logging/target/logging.war $WORKING_DIR/

cp -a $TESTING_HOME/script/all_scenarios.sh $WORKING_DIR/

echo "Install Python modules"
cd $WORKING_DIR

source $WORKING_DIR/venv/bin/activate


pip install pyparsing >> prepare_work.log
pip install requests >> prepare_work.log

echo "Working environment is ready"
echo "To continue using the environment, activate it with 'source $WORKING_DIR/venv/bin/activate && cd $WORKING_DIR'"