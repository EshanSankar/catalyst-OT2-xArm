SDL1 Automated Experiment System Construction Process
The core of this system is to receive experimental definitions in JSON format, drive multiple instruments to perform corresponding operations, and provide status feedback.


1.System Architecture


Core components:


WorkflowExecutor: Responsible for executing the workflow defined in JSON and managing OT-2 and Arduino devices
ExperimentDispatcher: responsible for distributing experimental requests to the corresponding backend modules
Backend module: Each experiment type (CVA, PEIS, OCV, etc.) has a dedicated backend implementation
ResultUploader: responsible for uploading and saving experimental results
Prefect integration: optional workflow management system that provides more advanced workflow control


Data Flow:
JSON workflow definition → WorkflowExecutor → Device control and experiment execution → Result collection and upload


Device Interaction:
OT-2 robot control (via HTTP API)
Arduino control (via serial port communication)
Electrochemical workstation control (such as Biologic)


2.Detailed explanation of the construction process


Step 1: Device Communication Layer
First, build the base layer for communicating with various experimental devices:


OT-2 robot communication:
Communicate with the OT-2 robot using the HTTP API
Realize basic operations such as moving, aspirating, discharging, etc.
Example code:
# OT-2 Communication Example
def moveToWell(self, labwareName, wellName, pipetteName, offsetX=0, offsetY=0, offsetZ=0):
   command = {
       "data": {
           "commandType": "moveToWell",
           "params": {
               "labwareId": self.labware[labwareName]["id"],
"wellName": wellName,
               "pipetteId": self.pipettes[pipetteName]["id"],
# Other parameters...
           }
       }
   }
   response = requests.post(
       url=self.commandURL,
       headers=self.headers,
       params={"waitUntilComplete": True},
       data=json.dumps(command)
   )


Arduino Communication:
Communicate with Arduino via Serial
Realize temperature control, pump control and other functions
Example code:
# Arduino Communication Example
def setTemp(self, baseNumber, targetTemp):
   self.connection.write(f"set_base_temp {baseNumber} {targetTemp}\n".encode())
# Waiting for response...


def dispense_ml(self, pumpNumber, volume):
# Control pump discharge...


Electrochemical workstation communication:
Implement the corresponding communication protocol according to the specific device
Supports various electrochemical measurement techniques (CV, PEIS, OCV, etc.)


Step 2: Backend module implementation
A specialized backend module needs to be implemented for each experiment type:


BaseBackend base class:
Provides basic functionality shared by all backends
Define a unified interface
Example code:
class BaseBackend(ABC):
   def __hot__(self, config_path=None, result_uploader=None, experiment_type="UNKNOWN"):
# Initialize...
  
   def connect_devices(self) -> bool:
# Connecting to the device...
  
   def execute_experiment(self, uo: Dict[str, Any]) -> Dict[str, Any]:
# Run the experiment...
  
   @abstractmethod
   def _execute_measurement(self, params: Dict[str, Any]) -> Dict[str, Any]:
# Methods that subclasses must implement


Specific experiment type backend:
Inheriting BaseBackend
Implementing logic for specific experiment types
Supported experiment types:
CVA (Cyclic Voltammetry)
PEIS (Electrochemical Impedance Spectroscopy)
OCV (Open Circuit Voltage)
CP (Constant Current Method)
LSV (Linear Sweep Voltammetry)
Example code:
class CVABackend(BaseBackend):
   def __hot__(self, config_path=None, result_uploader=None):
       super().__hot__(config_path, result_uploader, experiment_type="CVA")
  
   def _execute_measurement(self, params: Dict[str, Any]) -> Dict[str, Any]:
# Implement cyclic voltammetry measurement
       start_voltage = params["start_voltage"]
       end_voltage = params["end_voltage"]
       scan_rate = params["scan_rate"]
       cycles = params["cycles"]
      
# Perform measurements...
# Return results...


Step 3: Experiment Scheduler


The experiment scheduler is the core component of the system, responsible for distributing experiment requests to the corresponding backend modules:


ExperimentDispatcher class:
Manage backend instances for different types of experiments
Route requests to the corresponding backend according to the experiment type (uo_type)
Processing result upload and error handling
Example code:
class ExperimentDispatcher:
   def __hot__(self, config_path=None, result_uploader=None):
       self.backend_instances = {}
       self.result_uploader = result_uploader or LocalResultUploader()
  
   def _get_backend_instance(self, uo_type):
# Get or create a backend instance based on the experiment type
       backend_classes = {
           "CVA": CVABackend,
           "PEIS": PEISBackend,
           "OCV": OCVBackend,
           "CP": CPBackend,
           "LSV": LSVBackend
       }
      
       if uo_type not in backend_classes:
           raise ValueError(f"Unknown experiment type: {uo_type}")
      
# Create or return an existing instance...
  
   def execute_experiment(self, uo):
# Parsing parameters
# Generate experiment ID
# Get the backend instance
# Run the experiment
# Upload results


Result Uploader:
Responsible for saving and uploading experimental results
Supports local file system and remote storage (such as S3)
Example code:
class LocalResultUploader:
   def __hot__(self, base_dir="results"):
       self.base_dir = base_dir
       os.makedirs(base_dir, exist_ok=True)
  
   def upload(self, results, experiment_id):
# Save the results to the local file system


Step 4: Workflow Executor


The workflow executor is responsible for parsing and executing the workflow definition in JSON format:


WorkflowExecutor类:
Loading and parsing JSON workflow files
Execute the nodes and operations defined in the workflow
Supports two execution modes: direct execution and Prefect-based execution
Example code:
class WorkflowExecutor:
   def __hot__(self, workflow_file, use_prefect=False, mock_mode=False):
       self.workflow_file = workflow_file
       self.workflow = self._load_workflow(workflow_file)
# Initialize device client and operation dispatcher...
  
   def execute_workflow(self):
# Parsing workflow structure
# Find the starting node
# Execute the node and its child nodes


Workflow JSON format:
Define global configuration (labware, instruments, etc.)
Define nodes (experimental steps) and edges (relationships between nodes)
Each node contains OT-2 operation and Arduino control parameters
Example:
{
 "global_config": {
   "labware": { ... },
   "instruments": { ... }
 },
 "nodes": [
   {
     "id": "node1",
"label": "OCV experiment",
     "params": {


Prefect Integration:
Support more advanced workflow management
Provides functions such as retry, conditional execution, and manual intervention
You can register workflows to the Prefect server


Step 5: API and UI


Finally, you need to build an API and user interface to enable the system to receive and process experiment requests:


FastAPI interface:
Provide HTTP API interface to receive experimental requests
Forward the request to ExperimentDispatcher for processing
Example code:
@app.post("/run_experiment")
async def run_experiment(request: Request) -> Dict[str, Any]:
   try:
       uo = await request.json()
       logger.info(f"Received experiment request: {uo}")
      
# Run the experiment
       result = dispatcher.execute_experiment(uo)
      
       return {


Command line tools:
Provides command line tools to execute experiments and workflows
Supports different parameters and options
Example:
def run_experiment(args):
# Load the experiment file
   with open(args.experiment_file, 'r') as f:
       experiment = json.load(f)
  
# Create a scheduler
   dispatcher = ExperimentDispatcher()
  
# Run the experiment
   result = dispatcher.execute_experiment(experiment)
  
# Process the results...
Result visualization:
Save the experimental results in JSON format
Data visualization tools can be integrated to display results


3.Summary of the complete construction process
You summarize the construction process of the entire automated experiment system:


1.Device communication layer:
Implement HTTP API communication with OT-2 robot
Implementing serial communication with Arduino
Realize communication with electrochemical workstation
2.Backend modules:
Create a BaseBackend base class to define a common interface
Implement specialized backend classes for each experiment type
Implement experimental parameter verification and result processing
3.Experiment Scheduler:
Create the ExperimentDispatcher class to manage backend instances
Implementing routing and distribution of experimental requests
Implement result upload and error handling
4Workflow Executor:
Create a WorkflowExecutor class to parse and execute workflows
Define workflow JSON format
Implement the execution logic of nodes and operations
5.API and User Interface:
Create a FastAPI interface to receive HTTP requests
Create command line tools to execute experiments and workflows
Save and visualize results




The system is designed to be modular and can be easily expanded and customized:


Add new experiment type:
Create a new backend class that inherits BaseBackend
Implementing the _execute_measurement method
Registering a new backend class in the ExperimentDispatcher
Support for new devices:
Implementing the communication interface of new devices
Add support for new devices in BaseBackend
Enhanced workflow capabilities:
Add advanced features such as conditional execution and loops
Integrate more workflow management tools
Improved User Interface:
Creating a web interface for experiment design and monitoring
Add real-time data visualization capabilities

Modular design:
Maintain clear interfaces between components
Use dependency injection to simplify testing and replacing components
Error handling:
Implement comprehensive error handling and logging
Provide meaningful error messages and recovery mechanisms
Configuration Management:
Use configuration files to manage device parameters and default values
Support command line parameter override configuration
Tested and validated:
Write unit tests for each component
Integration testing with mock mode
Documentation and Examples:
Provide detailed API documentation
Contains example workflows and experiment definitions



