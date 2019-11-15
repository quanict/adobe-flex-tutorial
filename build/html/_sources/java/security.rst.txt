Security
========

.. toctree::
   :maxdepth: 0
   :caption: java_architecture

In many applications, access to some or all server-side resources must be restricted to certain users. Many Java EE applications use container managed security in which user authentication (validating a user) and user authorization (determining what the user has access to—which is often role based) are performed against the Realm, an existing store of usernames, passwords, and user roles. The Realm is configured on your Java EE server to be a relational database, an LDAP directory server, an XML document, or to use a specific authentication and authorization framework.

To integrate a Flex application with the Java EE security framework so that access to server-side resources is appropriately restricted, you add security information to the BlazeDS or LiveCycle Data Services configuration files (details follow below) and then typically in the Flex application, create a form to obtain login credentials from the user which are passed to the server to be authenticated. The user credentials are then passed to the server automatically with all subsequent requests.

Modifying services-config.xml
-----------------------------

In the BlazeDS or LiveCycle Data Services services-config.xml file, you need to specify the "login command" for your application server in the
<security>
tag. BlazeDS and LiveCycle Data Services supply the following login commands: TomcatLoginCommand (for both Tomcat and JBoss), JRunLoginCommand, WeblogicLoginCommand, WebSphereLoginCommand, OracleLoginCommand. These are all defined in the XML file and you just need to uncomment the appropriate one.

You also need to define a security constraint that you specify to use either basic or custom authentication and if desired,
one or more roles. To do custom authentication with Tomat or JBoss,
you also need to add some extra classes to the web application for integrating with the security framework used by the Jave EE application server and modify a couple of configuration files.
Mode details can be found `here <http://livedocs.adobe.com/blazeds/1/blazeds_devguide/>`__.

.. code::xml
    <services-config>    
        <security> 
        <login-command class="flex.messaging.security.TomcatLoginCommand"
            server="Tomcat">             
            <per-client-authentication>false</per-client-authentication>        
        </login-command> 
        <security-constraint id="trusted">         
            <auth-method>Custom</auth-method>         
            <roles>             
                <role>employees</role>             
                <role>managers</role>         
            </roles>     
            </security-constraint> 
        </security>  
        ... 
    </services-config>

Modifying remoting-config.xml
-----------------------------

Next, in your destination definition, you need to reference the security constraint:

.. code::xml
    <destination id="employeeService">
        <properties>
        <source>services.EmployeeService</source>
        </properties>
        <security>
        <security-constraint ref="trusted"/>
        </security> 
    </destination>

You can also define default security constraints for all destinations and/or restrict access to only specific methods that can use different security constraints.

The default channel, my-amf, uses HTTP. You can change one or more of the destinations to use the my-secure-amf channel that uses HTTPS:

.. code::xml
    <destination id="employeeService">     
        <channels>         
            <channel ref="my-secure-amf"/>     
        </channels> 
        ... 
    </destination>

where `my-secure-amf` is defined in the `services-config.xml` file:

.. code::xml
<!-- Non-polling secure AMF --> 
    <channel-definition id="my-secure-amf" class="mx.messaging.channels.SecureAMFChannel">    
        <endpoint url="https://{server.name}:{server.port}/{context.root}/messagebroker/amfsecure" class="flex.messaging.endpoints.SecureAMFEndpoint"/> 
    </channel-definition> 

Adding code to the Flex application
-----------------------------------

That covers the server-side setup.
Now, if you are using custom authentication,
you need to create a form in the Flex application to retrieve a username and password from the user and then pass these credentials 
to the server by calling the **ChannelSet.login()** method
and then listening for its **result** and **fault** events.
A result event indicates that the login (the authentication) occurred successfully, and a **fault** event indicates the login failed.
The credentials are applied to all services connected over the same ChannelSet.
For basic authentication, you don’t have to add anything to your Flex application. The browser opens a login dialog box when the application first attempts to connect to a destination.

Your application can now make Flash Remoting requests to server destinations just as before, but now the user credentials are automatically sent with every request (for both custom and basic authentication). If the destination or methods of the destination have authorization roles specified which are not met by the logged in user, the call will return a fault event. To remove the credentials and log out the user, you use the ChannelSet.logout() method.

