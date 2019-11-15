Flex application architecture
=============================

.. toctree::
   :maxdepth: 0
   :caption: java_architecture

Now that you've learned to set up Flash Remoting on the server-side and define a RemoteObject instance in Flex, let's take a look at how you build an application to use this object.

Using events
------------

A typical Flex application consists of MXML code to define the user interface and ActionScript code for the logic. Just as for JavaScript and the browser DOM objects, the two are wired together using events and event handlers. To use a RemoteObject in an application, you define the instance, invoke a method of the server-side remoting destination, specify callback functions for the result and fault events, and inside those, do something with the data returned from the server.

Here is a simple application where employee data is retrieved from a database and displayed in a Flex DataGrid component. After the application is initialized, the getEmployees() method of the employeeService destination defined in the remoting-config.xml file on the server is called, and if data is successfully returned from the server, the variable employees is populated and if the request fails for any reason, a message is displayed in an Alert box. Data binding is used to bind the employees variable to the dataProvider property of the DataGrid.

.. code::xml
    <s:Application xmlns:fx="http://ns.adobe.com/mxml/2009"
    xmlns:s="library://ns.adobe.com/flex/spark"
    xmlns:mx="library://ns.adobe.com/flex/mx"            
    initialize="employeeSvc.getEmployees()">
        <fx:Script>
            <![CDATA[
                import mx.collections.ArrayCollection;
                import mx.controls.Alert;
                import mx.rpc.events.FaultEvent;
                import mx.rpc.events.ResultEvent;
                [Bindable]private var employees:ArrayCollection;
                private function onResult(e:ResultEvent):void{
                    employees=e.result as ArrayCollection;               
                }
                private function onFault(e:FaultEvent):void{
                    Alert.show("Error retrieving data.","Error");
                }
            ]]>
        </fx:Script>
        <fx:Declarations>
            <s:RemoteObject id="employeeSvc" destination="employeeService"
                result="onResult(event)" fault="onFault(event)" />
        </fx:Declarations>
        <mx:DataGrid dataProvider="{employees}"/>
    </s:Application>

When using a RemoteObject, you can define `result and fault handlers on the service level`:

.. code::xml
    <s:RemoteObject id="employeeSvc" destination="employeeService" result="onResult(event)" fault="onFault(event)"/>

on the method level:
.. code::xml
    <s:RemoteObject id="employeeSvc" destination="employeeService">
        <s:method name="getEmployees" result="onResult(event)" fault="onFault(event)"/>
        <s:method name="getDepartments" result="onResult2(event)" fault="onFault2(event)"/>
    </RemoteObject>

or on a per-call basis:
.. code::xml
    <s:Application xmlns:fx=http://ns.adobe.com/mxml/2009"
    xmlns:s="library://ns.adobe.com/flex/spark"               
    xmlns:mx="library://ns.adobe.com/flex/mx"
    initialize="getEmployeesResult.token=employeeSvc.getEmployees()">
        <fx:Declarations>
            <s:RemoteObject id="employeeSvc" destination="employeeService"/>
            <s:CallResponder id="getEmployeesResult" result="onResult(event)"
                fault="onFault(event)"/>
        </fx:Declarations>

Using data binding
------------------

Data binding is a powerful part of the Flex framework that lets you update the user interface when data changes without you having to explicitly register and write the event listeners to do this. In the previous application code, the [Bindable] tag in front of the employees variable definition is a compiler directive; when the file is compiled, ActionScript code is automatically generated so that an event is broadcast whenever the employees variable changes.

.. code::flex
    [Bindable]private var employees:ArrayCollection;

The curly braces in the assignment of the DataGrid's dataProvider property actually generates the code to listen for changes to the employees variable and when it changes, to update the DataGrid view accordingly.

.. code::xml
    <mx:DataGrid dataProvider="{employees}"/>

In this application, employees is initially null and no data is displayed in the DataGrid but as soon as the data is successfully retrieved form the server and employees is populated, the DataGrid is updated to display the employee data.

Using view states
-----------------

To make more extreme changes to the user interface dynamically at runtime,
for instance to add, remove, move, or modify components,
you use Flex `view states <http://help.adobe.com/en_US/Flex/4.0/UsingSDK/WS2db454920e96a9e51e63e3d11c0bf69084-7fb4.html>`__.
For every Flex view or component, you can define multiple states and then for every object in that view,
you can define what state(s) it should be included in and what it should look like and how it should behave in that state.
You switch between states by setting the component's currentState property to the name of one of the defined states.

.. code::xml

    <s:states>
        <s:State name="employees"/>
        <s:State name="departments"/>
    /s:states>
    <mx:DataGrid dataProvider="{employees}" includeIn="employees"/>
    <s:Button label.employees="Switch to departments" label.departments="Switch to employees" click.employees="currentState='departments'" click.departments="currentState='employees'"/>

Using MXML components
---------------------

As your application gets larger, you need to break up your logic into packages of ActionScript classes and your views into separate MXML files (called MXML components). Each MXML component extends an existing component and can only be included in an application, but not run on its own. To use a component in MXML, you instantiate an instance of that component (its class name is the same as its file name) and include the proper namespace so the compiler can locate it.

Here is the code for a MXML component, Masterview, saved as MasterView.mxml in the com.adobe.samples.views package.

.. code::xml
    <s:Group xmlns:fx="http://ns.adobe.com/mxml/2009"
    xmlns:s="library://ns.adobe.com/flex/spark" >
        <fx:Metadata>
            [Event(name="masterDataChange",type="flash.events.Event")]
        </fx:Metadata>
        <fx:Script>
            <![CDATA[
                import mx.collections.ArrayList;
                [Bindable]private var masterData:ArrayList=new ArrayList(["data1", "data2", "data3"]);
                public var selectedData:String;
                private function onChange(e:Event):void{
                selectedData=dataList.selectedItem;
                this.dispatchEvent(new Event("masterDataChange"));
                }
            ]]>
        </fx:Script>
        <s:DropDownList id="dataList" dataProvider="{masterData}" change="onChange(event)"/>
    </s:Group>

Here is the code for an application that instantiates and uses that custom MasterView component.

.. code::xml
    <s:Application xmlns:fx="http://ns.adobe.com/mxml/2009"
    xmlns:s="library://ns.adobe.com/flex/spark"
    xmlns:views="com.adobe.samples.views.*">
        <fx:Script>
            <![CDATA[
                import mx.controls.Alert;
                private function onMasterDataChange(e:Event):void{
                Alert.show(e.currentTarget.selectedData,"Master data changed");
                }
            ]]>
        </fx:Script>
        <views:MasterView masterDataChange="onMasterDataChange(event)"/>
    </s:Application>

Broadcasting events
-------------------

In order to build loosely-coupled components,
you need to define a public API for the component (its public members)
and/or define and broadcast custom events as shown in the MasterView code example above.
The [**Event**] metadata tag is used to define the event as part of the component's API and specify what type of event object it broadcasts.

.. code::xml
    <fx:Metadata>
        [Event(name="masterDataChange",type="flash.events.Event")]
    </fx:Metadata>

When some event occurs in the component (in this example, a DropDownList **change** event),
the component creates an instance of the type of event object specified in the metadata and broadcasts it.

.. code::flex
    this.dispatchEvent(new Event("masterDataChange"));

The code that instantiates this custom component can now register to listen for this custom event and register and event handler.

.. code::flex
    <views:MasterView masterDataChange="onMasterDataChange(event)"/>

Loosely-coupled components like this that define and broadcast custom events are the core building blocks for Flex applications.
In fact, this is how the components in the Flex framework itself are built.
For more information on broadcasting custom events, watch the video,
Learn how to `define and broadcast events <http://tv.adobe.com/watch/adc-presents/define-events-in-flex-4-with-flash-builder-4/>`__.

Creating modules
----------------

By default, all your code gets compiled into one SWF file.
If your SWF file gets very large or contains functionality that only specific users may use,
you can use `modules <http://help.adobe.com/en_US/Flex/4.0/UsingSDK/WS2db454920e96a9e51e63e3d11c0bf69084-799a.html>`__ to break your application into multiple SWF files that can be loaded
and unloaded dynamically by the main application at runtime.
To create a module, you create a class (ActionScript of MXML) extending the Module class and then compile it.
To load the module dynamically at runtime into an application,
you use the **<mx:ModuleLoader>** tag or methods of the ModuleLoader class.

Using a microarchitecture
-------------------------

That covers the basics for building an application,
but as your application gets larger, you are going to want to use some methodology to organize its files, centralize the application data and data services, and handle communication between all the components. To do this, you can build your Flex application using all the design patterns that have proven useful over the years in enterprise application development. In fact, many Flex specific microarchitectures have been and continue to be developed. The oldest and most established is Cairngorm, an open source microarchitecture that uses commands and delegates, front controllers, a singleton data model, a singleton service store, and an event dispatcher. Other popular frameworks include Pure MVC, Mate, Parsley, Swiz, and Spring ActionScript. For more information about these and other frameworks, see Flex Architecture on the Adobe Developer Center.











