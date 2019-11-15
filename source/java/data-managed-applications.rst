Data managed applications
=========================

.. toctree::
   :maxdepth: 0
   :caption: java_architecture

You can build real-time data applications, applications for which data changes made in one client are "instantly" seen by other clients viewing the same data, using a combination of remoting and messaging. This entails writing a lot of client-side code to keep track of the changes made to the data on the client (additions, updates, and deletions), to make calls to retrieve and persist data on the server, to send messages to other clients when the data has changed, to make calls to retrieve and display this new data, to recognize and handle data conflicts, and to resolve these conflicts on the client and server. To help you more quickly and easily build these types of data-intensive, transaction-oriented applications without having to write so much code. LiveCycle Data Services (and not BlazeDS) provides the Data Management service.

The Data Management service provides client and server-side code to help you build applications that provide real-time data synchronization between client, server, and other clients; data replication; on-demand data paging; and for AIR applications, local data synchronization for occasionally connected applications.

To build a managed data application you define a Data Management service destination in a configuration file on the server and then use the Flex DataService component in the application to call methods of a server-side service specified by that destination. The DataService API provides methods for filling client-side data collections with data from the server and batching and sending data changes to the server. The Data Management service on the server handles checking for conflicts, committing the changes, and pushing the data changes to simultaneously connected clients.

Defining destinations
---------------------

Similar to how you configure remoting and messaging,
you typically configure data management by defining destinations in a server-side configuration file,
in this case,
data-management-config.xml.
The default configuration file defines a default channel,
the RTMP channel discussed in `Selecting a channel <http://flex_java_architecture_06.html/#selecting>`__ in the Messaging section of this article,
and a default adapter, **actionscript**.

.. code::xml
    <service id="data-service"
        class="flex.data.DataService">
        <adapters>
            <adapter-definition id="actionscript" class="flex.data.adapters.ASObjectAdapter" default="true"/>
            <adapter-definition id="java-dao" class="flex.data.adapters.JavaAdapter"/>
        </adapters>
        <default-channels>
            <channel ref="my-rtmp"/>
        </default-channels>
    </service>

The adapter is responsible for updating the server-side data.
The actionscript adapter is used for services that have no persistent data store on the server but instead manage data in the server's memory.
The **java-dao** adapter passes the data changes to appropriate methods of a Java assembler class, which typically calls methods of a data access object (DAO) to persist data in a database.

When defining a destination using the java-dao adapter,
you specify the assembler class that handles the data persistence and the property of the data objects that uniquely identifies an object.
Below is a data management destination called employeeService that uses a Java class called EmployeeAssembler
to persist data in a database table with a unique field employeeId.
The Java assembler class must extend an AbstractAssembler class provided with LiveCycle Data Services
that has methods including **fill()**, **createItem()**, **deleteItem()**, and **updateItem()**.

.. code::xml
    <destination id="employeeService">
        <adapter ref="java-dao"/>
        <properties>
            <source>adobe.samples.EmployeeAssembler</source>
            <metadata>
                <identity property="employeeId"/>
            </metadata>
        </properties>
    </destination>

You can add additional properties to the destination definition to specify the scope the assembler is available in (request, session, or application), to configure paging, to specify security-constraints, and more.

LiveCycle Data Services also provides some standard assembler classes that you can use so you don’t have to write your own. The SQLAssembler provides a bridge to a SQL database without requiring you to write the Java assembler code. Instead, you specify database info (url, driver, username, password, etc.) and SQL statements (the SQL to execute when data is sent from the Flex application to be added, updated, or deleted) right in the destination definition. This assembler can be used for simple database models that do not have any nested relationships. If you are using Hibernate, you can use the HibernateAssembler, which provides a bridge to the Hibernate object/relational persistence and query service. It uses the Hibernate mapping files to at runtime to execute the necessary SQL to persist data changes to the database.

Creating a managed data application
-----------------------------------

To create a Flex managed data application that uses the LCDS Data Management service, you create a DataService object with its destination property set to a destination defined in the data-management-config.xml file. You use the DataService fill() method to fetch data from the server and populate an ArrrayCollection with the data. By default, the DataService commit() method is called whenever data changes in the ArrayCollection it manages. To avoid excessive calls, you can batch the calls by setting the DataService object's autoCommit property to false and then explicitly calling its commit() method.

Here is a simple application that uses the employeeService Data Management destination to retrieve employee data from the database on the server and populate a DataGrid with that data. When changes are made to the data in the DataGrid, the changes are automatically persisted on the server and synchonized with any other instances of the client application.

.. code::xml
    <s:Application xmlns:fx="http://ns.adobe.com/mxml/2009"
        xmlns:s="library://ns.adobe.com/flex/spark"
        xmlns:mx="library://ns.adobe.com/flex/mx"
        xmlns:valueObjects="valueObjects.*"
        creationComplete="employeeDS.fill(employees)">
        <fx:Declarations>
            <s:DataService id="employeeDS" destination="employeeService"/>
            <s:ArrayCollection id="employees"/>
            <valueObjects:Employee id="employee"/>
        </fx:Declarations>
        <mx:DataGrid dataProvider="{employees}" editable="true"/>
    </s:Application>

For more information about using the Data Management service, see the `Live Cycle Data Services <http://help.adobe.com/en_US/LiveCycleDataServicesES/3.0/Developing/WSC04AFC0E-5BF5-4c2f-8A32-BEDE16E9DF95.html>`__ documentation.

