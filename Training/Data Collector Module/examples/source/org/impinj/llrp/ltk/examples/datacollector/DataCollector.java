package org.impinj.llrp.ltk.examples.datacollector;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.IOException;
import java.math.BigInteger;
import java.util.ArrayList;
import java.io.FileReader;
import java.util.concurrent.TimeoutException;
import java.util.List;
import java.util.Scanner;
import java.util.Arrays;
import java.util.HashMap;
import java.io.BufferedReader;

import org.apache.log4j.BasicConfigurator;
import org.apache.log4j.Level;
import org.apache.log4j.Logger;
import org.jdom.JDOMException;

import org.llrp.ltk.exceptions.*;
import org.llrp.ltk.generated.enumerations.*;
import org.llrp.ltk.generated.interfaces.*;
import org.llrp.ltk.generated.messages.*;
import org.llrp.ltk.generated.parameters.*;
import org.llrp.ltk.types.*;
import org.llrp.ltk.net.LLRPConnection;
import org.llrp.ltk.net.LLRPConnectionAttemptFailedException;
import org.llrp.ltk.net.LLRPConnector;
import org.llrp.ltk.net.LLRPEndpoint;
import org.llrp.ltk.util.Util;

import org.llrp.ltk.generated.custom.enumerations.*;
import org.llrp.ltk.generated.custom.messages.*;
import org.llrp.ltk.generated.custom.parameters.*;

import java.sql.Timestamp;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Iterator;
import java.util.Map;
import java.util.Scanner;
import java.util.stream.Stream;

import com.mongodb.BasicDBObject;
import com.mongodb.DB;
import com.mongodb.DBCollection;
import com.mongodb.DBObject;
import com.mongodb.MongoClient;
import com.mongodb.MongoClientURI;

import java.util.concurrent.TimeUnit;

/*
 * 
 * CLASS: DataCollector
 * 
 */
public class DataCollector implements LLRPEndpoint {
	
    private LLRPConnection connection;
    
    static DataInterface di = new DataInterface();
    static int numSnapshots = 3600;
    static int sleepTime = 1000;

    private static Logger logger  = Logger.getLogger("org.impinj.llrp.ltk.examples.datacollector");
    private ROSpec rospec;
    private int MessageID = 23; // a random starting point
    private UnsignedInteger modelName;
    UnsignedShort maxPowerIndex;
    SignedShort maxPower;
    UnsignedShort channelIndex;
    UnsignedShort hopTableID;

    // stuff to calculate velocity
    String        lastEPCData;
    UnsignedShort lastAntennaID;
    UnsignedShort lastChannelIndex;
    UnsignedLong  lastReadTime;
    String        currentEPCData;
    UnsignedShort currentAntennaID;
    UnsignedShort currentChannelIndex;
    UnsignedLong  currentReadTime;
    double        lastRfPhase;
    double        currentRfPhase;

    private UnsignedInteger getUniqueMessageID() {
        return new UnsignedInteger(MessageID++);
    }

    public DataCollector() {
        lastEPCData = null;
        lastAntennaID = new UnsignedShort(0);
        lastChannelIndex = new UnsignedShort(0);
        lastReadTime = new UnsignedLong(0L);
        lastRfPhase = 0;
    }

    private void connect(String ip) {
        // create client-initiated LLRP connection

        connection = new LLRPConnector(this, ip);

        // connect to reader
        // LLRPConnector.connect waits for successful
        // READER_EVENT_NOTIFICATION from reader
        try {
            logger.info("Initiate LLRP connection to reader");
            ((LLRPConnector) connection).connect();
        } catch (LLRPConnectionAttemptFailedException e1) {
            e1.printStackTrace();
            System.exit(1);
        }
    }

    private void disconnect() {
        LLRPMessage response;
        CLOSE_CONNECTION close = new CLOSE_CONNECTION();
        close.setMessageID(getUniqueMessageID());
        try {
            // don't wait around too long for close
            response = connection.transact(close, 4000);

            // check whether ROSpec addition was successful
            StatusCode status = ((CLOSE_CONNECTION_RESPONSE)response).getLLRPStatus().getStatusCode();
            if (status.equals(new StatusCode("M_Success"))) {
                logger.info("CLOSE_CONNECTION was successful");
            }
            else {
                logger.info(response.toXMLString());
                logger.info("CLOSE_CONNECTION Failed ... continuing anyway");
            }
        } catch (InvalidLLRPMessageException ex) {
            logger.error("CLOSE_CONNECTION: Received invalid response message");
        } catch (TimeoutException ex) {
            logger.info("CLOSE_CONNECTION Timeouts ... continuing anyway");
        } finally {
			((LLRPConnector)connection).disconnect();
		}
    }

    private void enableImpinjExtensions() {
        LLRPMessage response;

        try {
            logger.info("IMPINJ_ENABLE_EXTENSIONS ...");
            IMPINJ_ENABLE_EXTENSIONS ena = new IMPINJ_ENABLE_EXTENSIONS();
            ena.setMessageID(getUniqueMessageID());

            response =  connection.transact(ena, 10000);

            StatusCode status = ((IMPINJ_ENABLE_EXTENSIONS_RESPONSE)response).getLLRPStatus().getStatusCode();
            if (status.equals(new StatusCode("M_Success"))) {
                    logger.info("IMPINJ_ENABLE_EXTENSIONS was successful");
            }
            else {
                    logger.info(response.toXMLString());
                    logger.info("IMPINJ_ENABLE_EXTENSIONS Failure");
                    System.exit(1);
            }
        } catch (InvalidLLRPMessageException ex) {
            logger.error("Could not process IMPINJ_ENABLE_EXTENSIONS response");
            System.exit(1);
        } catch (TimeoutException ex) {
            logger.error("Timeout Waiting for IMPINJ_ENABLE_EXTENSIONS response");
            System.exit(1);
        }
    }

    private void factoryDefault() {
        LLRPMessage response;

        try {
            // factory default the reader
            logger.info("SET_READER_CONFIG with factory default ...");
            SET_READER_CONFIG set = new SET_READER_CONFIG();
            set.setMessageID(getUniqueMessageID());
            set.setResetToFactoryDefault(new Bit(true));
            response =  connection.transact(set, 10000);

            // check whether ROSpec addition was successful
            StatusCode status = ((SET_READER_CONFIG_RESPONSE)response).getLLRPStatus().getStatusCode();
            if (status.equals(new StatusCode("M_Success"))) {
                    logger.info("SET_READER_CONFIG Factory Default was successful");
            }
            else {
                    logger.info(response.toXMLString());
                    logger.info("SET_READER_CONFIG Factory Default Failure");
                    System.exit(1);
            }

        } catch (Exception e) {
            e.printStackTrace();
            System.exit(1);
        }
    }

    private void getReaderCapabilities() {
        LLRPMessage response;
        GET_READER_CAPABILITIES_RESPONSE gresp;

        GET_READER_CAPABILITIES get = new GET_READER_CAPABILITIES();
        GetReaderCapabilitiesRequestedData data = 
                new GetReaderCapabilitiesRequestedData(
                        GetReaderCapabilitiesRequestedData.All);
        get.setRequestedData(data);
        get.setMessageID(getUniqueMessageID());
        logger.info("Sending GET_READER_CAPABILITIES message  ...");
        try {
            response =  connection.transact(get, 10000);

            // check whether GET_CAPABILITIES addition was successful
            gresp = (GET_READER_CAPABILITIES_RESPONSE)response;
            StatusCode status = gresp.getLLRPStatus().getStatusCode();
            if (status.equals(new StatusCode("M_Success"))) {
                logger.info("GET_READER_CAPABILITIES was successful");

                // get the info we need
                GeneralDeviceCapabilities dev_cap = gresp.getGeneralDeviceCapabilities();
                if ((dev_cap == null) ||
                    (!dev_cap.getDeviceManufacturerName().equals(new UnsignedInteger(25882)))) {
                    logger.error("DataCollector must use Impinj model Reader, not " +
                        dev_cap.getDeviceManufacturerName().toString());
                    System.exit(1);
                }

                modelName = dev_cap.getModelName();
                logger.info("Found Impinj reader model " + modelName.toString());

                // get the max power level
                if( gresp.getRegulatoryCapabilities() != null) {
                    UHFBandCapabilities band_cap =
                        gresp.getRegulatoryCapabilities().getUHFBandCapabilities();

                    List<TransmitPowerLevelTableEntry> pwr_list = 
                        band_cap.getTransmitPowerLevelTableEntryList();

                    TransmitPowerLevelTableEntry entry =
                        pwr_list.get(pwr_list.size() - 1);

                    maxPowerIndex = entry.getIndex();
                    maxPower = entry.getTransmitPowerValue();
                    // LLRP sends power in dBm * 100
                    double d = ((double) maxPower.intValue())/100;

                    logger.info("Max power " + d +
                                " dBm at index " + maxPowerIndex.toString());
                }
            }
            else {
                logger.info(response.toXMLString());
                logger.info("GET_READER_CAPABILITIES failures");
                System.exit(1);
            }
        } catch (InvalidLLRPMessageException ex) {
            logger.error("Could not display response string");
        } catch (TimeoutException ex) {
            logger.error("Timeout waiting for GET_READER_CAPABILITIES response");
            System.exit(1);
        }
    }

    private void getReaderConfiguration() {
        LLRPMessage response;
        GET_READER_CONFIG_RESPONSE gresp;

        GET_READER_CONFIG get = new GET_READER_CONFIG();
        GetReaderConfigRequestedData data =
                new GetReaderConfigRequestedData(
                        GetReaderConfigRequestedData.All);
        get.setRequestedData(data);
        get.setMessageID(getUniqueMessageID());
        get.setAntennaID(new UnsignedShort(0));
        get.setGPIPortNum(new UnsignedShort(0));
        get.setGPOPortNum(new UnsignedShort(0));

        logger.info("Sending GET_READER_CONFIG message  ...");
        try {
            response =  connection.transact(get, 10000);

            // check whether GET_CAPABILITIES addition was successful
            gresp = (GET_READER_CONFIG_RESPONSE)response;
            StatusCode status = gresp.getLLRPStatus().getStatusCode();
            if (status.equals(new StatusCode("M_Success"))) {
                logger.info("GET_READER_CONFIG was successful");

                List<AntennaConfiguration> alist = gresp.getAntennaConfigurationList();

                if(!alist.isEmpty()) {
                    AntennaConfiguration a_cfg = alist.get(0);
                    channelIndex  = a_cfg.getRFTransmitter().getChannelIndex();
                    hopTableID =  a_cfg.getRFTransmitter().getHopTableID();
                    logger.info("ChannelIndex " + channelIndex.toString() +
                                " hopTableID " + hopTableID.toString());
                } else {
                    logger.error("Could not find antenna configuration");
                    System.exit(1);
                }
            }
            else {
                logger.info(response.toXMLString());
                logger.info("GET_READER_CONFIG failures");
                System.exit(1);
            }
        } catch (InvalidLLRPMessageException ex) {
            logger.error("Could not display response string");
        } catch (TimeoutException ex) {
            logger.error("Timeout waiting for GET_READER_CONFIG response");
            System.exit(1);
        }
    }

    private ADD_ROSPEC buildROSpecFromObjects() {
        logger.info("Building ADD_ROSPEC message from scratch ...");
        ADD_ROSPEC addRoSpec = new ADD_ROSPEC();
        addRoSpec.setMessageID(getUniqueMessageID());

        rospec = new ROSpec();

        // set up the basic info for the RO Spec.
        rospec.setCurrentState(new ROSpecState(ROSpecState.Disabled));
        rospec.setPriority(new UnsignedByte(0));
        rospec.setROSpecID(new UnsignedInteger(12345));

        // set the start and stop conditions for the ROSpec.
        // For now, we will start and stop manually 
        ROBoundarySpec boundary = new ROBoundarySpec();
        ROSpecStartTrigger start = new ROSpecStartTrigger();
        ROSpecStopTrigger stop = new ROSpecStopTrigger();
        start.setROSpecStartTriggerType(new ROSpecStartTriggerType(ROSpecStartTriggerType.Null));
        stop.setROSpecStopTriggerType(new ROSpecStopTriggerType(ROSpecStopTriggerType.Null));
        stop.setDurationTriggerValue(new UnsignedInteger(0));
        boundary.setROSpecStartTrigger(start);
        boundary.setROSpecStopTrigger(stop);
        rospec.setROBoundarySpec(boundary);

        // set up what we want to do in the ROSpec. In this case
        // build the simplest inventory on all channels using defaults
        AISpec aispec = new AISpec();

        // what antennas to use.
        UnsignedShortArray ants = new UnsignedShortArray();
        ants.add(new UnsignedShort(0)); // 0 means all antennas
        aispec.setAntennaIDs(ants);

        // set up the AISpec stop condition and options for inventory
        AISpecStopTrigger aistop = new AISpecStopTrigger();
        aistop.setAISpecStopTriggerType(new AISpecStopTriggerType(AISpecStopTriggerType.Null));
        aistop.setDurationTrigger(new UnsignedInteger(0));
        aispec.setAISpecStopTrigger(aistop);

        // set up any override configuration.  none in this case
        InventoryParameterSpec ispec = new InventoryParameterSpec();
        ispec.setAntennaConfigurationList(null);
        ispec.setInventoryParameterSpecID(new UnsignedShort(23));
        ispec.setProtocolID(new AirProtocols(AirProtocols.EPCGlobalClass1Gen2));
        List<InventoryParameterSpec> ilist = new ArrayList<InventoryParameterSpec>();
        ilist.add(ispec);

        aispec.setInventoryParameterSpecList(ilist);
        List<SpecParameter> slist = new ArrayList<SpecParameter>();
        slist.add(aispec);
        rospec.setSpecParameterList(slist);

        addRoSpec.setROSpec(rospec);

        return addRoSpec;
    }

    private ADD_ROSPEC buildROSpecFromFile() {
        logger.info("Loading ADD_ROSPEC message from file ADD_ROSPEC.xml ...");
        try {
            LLRPMessage addRospec = Util.loadXMLLLRPMessage(new File("./source/org/impinj/llrp/ltk/examples/datacollector/ADD_ROSPEC.xml"));
            // TODO make sure this is an ADD_ROSPEC message 
            return (ADD_ROSPEC) addRospec;
        } catch (FileNotFoundException ex) {
            logger.error("Could not find file");
            System.exit(1);
        } catch (IOException ex) {
            logger.error("IO Exception on file");
            System.exit(1);
        } catch (JDOMException ex) {
            logger.error("Unable to convert LTK-XML to DOM");
            System.exit(1);
        } catch (InvalidLLRPMessageException ex) {
            logger.error("Unable to convert LTK-XML to Internal Object");
            System.exit(1);
        }
        return null;
    }

    private void setReaderConfiguration() {
        LLRPMessage response;
        
        logger.info("Loading SET_READER_CONFIG message from file SET_READER_CONFIG.xml ...");

        try {
            LLRPMessage setConfigMsg = Util.loadXMLLLRPMessage(
            new File("./source/org/impinj/llrp/ltk/examples/datacollector/SET_READER_CONFIG.xml"));
            // TODO make sure this is an SET_READER_CONFIG message

            response = connection.transact(setConfigMsg, 10000);
            
            // check whetherSET_READER_CONFIG addition was successful
            StatusCode status = ((SET_READER_CONFIG_RESPONSE)response).getLLRPStatus().getStatusCode();
            if (status.equals(new StatusCode("M_Success"))) {
                    logger.info("SET_READER_CONFIG was successful");
            }
            else {
                    logger.info(response.toXMLString());
                    logger.info("SET_READER_CONFIG failures");
                    System.exit(1);
            }

        } catch (TimeoutException ex) {
            logger.error("Timeout waiting for SET_READER_CONFIG response");
            System.exit(1);
        } catch (FileNotFoundException ex) {
            logger.error("Could not find file");
            System.exit(1);
        } catch (IOException ex) {
            logger.error("IO Exception on file");
            System.exit(1);
        } catch (JDOMException ex) {
            logger.error("Unable to convert LTK-XML to DOM");
            System.exit(1);
        } catch (InvalidLLRPMessageException ex) {
            logger.error("Unable to convert LTK-XML to Internal Object");
            System.exit(1);
        }
    }

    private void addRoSpec(boolean xml) {
        LLRPMessage response;

        ADD_ROSPEC addRospec = null;

        if(xml) {
            addRospec = buildROSpecFromFile();
        } else {
            addRospec = buildROSpecFromObjects();
        }

        addRospec.setMessageID(getUniqueMessageID());
        rospec = addRospec.getROSpec();
        
        logger.info("Sending ADD_ROSPEC message  ...");
        try {
            response =  connection.transact(addRospec, 10000);

            // check whether ROSpec addition was successful
            StatusCode status = ((ADD_ROSPEC_RESPONSE)response).getLLRPStatus().getStatusCode();
            if (status.equals(new StatusCode("M_Success"))) {
                    logger.info("ADD_ROSPEC was successful");
            }
            else {
                    logger.info(response.toXMLString());
                    logger.info("ADD_ROSPEC failures");
                    System.exit(1);
            }
        } catch (InvalidLLRPMessageException ex) {
            logger.error("Could not display response string");
        } catch (TimeoutException ex) {
            logger.error("Timeout waiting for ADD_ROSPEC response");
            System.exit(1);
        }
    }

    private void enable() {
        LLRPMessage response;
        try {
            // factory default the reader
            logger.info("ENABLE_ROSPEC ...");
            ENABLE_ROSPEC ena = new ENABLE_ROSPEC();
            ena.setMessageID(getUniqueMessageID());
            ena.setROSpecID(rospec.getROSpecID());

            response =  connection.transact(ena, 10000);

            // check whether ROSpec addition was successful
            StatusCode status = ((ENABLE_ROSPEC_RESPONSE)response).getLLRPStatus().getStatusCode();
            if (status.equals(new StatusCode("M_Success"))) {
                    logger.info("ENABLE_ROSPEC was successful");
            }
            else {
                    logger.error(response.toXMLString());
                    logger.info("ENABLE_ROSPEC_RESPONSE failed ");
                    System.exit(1);
            }
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(1);
        }
    }

    private void start() {
        LLRPMessage response;
        try {
            logger.info("START_ROSPEC ...");
            START_ROSPEC start = new START_ROSPEC();
            start.setMessageID(getUniqueMessageID());
            start.setROSpecID(rospec.getROSpecID());

            response =  connection.transact(start, 10000);

            // check whether ROSpec addition was successful
            StatusCode status = ((START_ROSPEC_RESPONSE)response).getLLRPStatus().getStatusCode();
            if (status.equals(new StatusCode("M_Success"))) {
                    logger.info("START_ROSPEC was successful");
            }
            else {
                    logger.error(response.toXMLString());
                    logger.info("START_ROSPEC_RESPONSE failed ");
                    System.exit(1);
            }
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(1);
        }
    }

    private void stop() {
        LLRPMessage response;
        try {
            logger.info("STOP_ROSPEC ...");
            STOP_ROSPEC stop = new STOP_ROSPEC();
            stop.setMessageID(getUniqueMessageID());
            stop.setROSpecID(rospec.getROSpecID());

            response =  connection.transact(stop, 10000);

            // check whether ROSpec addition was successful
            StatusCode status = ((STOP_ROSPEC_RESPONSE)response).getLLRPStatus().getStatusCode();
            if (status.equals(new StatusCode("M_Success"))) {
                    logger.info("STOP_ROSPEC was successful");
            }
            else {
                    logger.error(response.toXMLString());
                    logger.info("STOP_ROSPEC_RESPONSE failed ");
                    System.exit(1);
            }
        } catch (Exception e) {
            e.printStackTrace();
            System.exit(1);
        }
    }

    private void logOneCustom(Custom cust) {

        String output = "";
        if(!cust.getVendorIdentifier().equals(25882)) {
            logger.error("Non Impinj Extension Found in message");
            return;
        }
    }

    private void logOneTagReport(TagReportData tr) {
        // As an example here, we'll just get the stuff out of here and
        // for a super long string

        LLRPParameter epcp = (LLRPParameter) tr.getEPCParameter();
        
    	String EPC = "0000";
    	long lastUpdated = 0;
        String antenna = "0";
        String channel = "0";
        String firstSeen = "0";
        String lastSeen = "0";
        String peakRSSI = "0";
        String seenCount = "0";
        int phaseAngle = 0;
        String velocity = "0";

        // epc is not optional, so we should fail if we can't find it
        if(epcp != null) {
            if( epcp.getName().equals("EPC_96")) {
                EPC_96 epc96 = (EPC_96) epcp;
                EPC = epc96.getEPC().toString();
                currentEPCData = epc96.getEPC().toString();
            } else if ( epcp.getName().equals("EPCData")) {
                EPCData epcData = (EPCData) epcp;
                EPC = epcData.getEPC().toString();
                currentEPCData = epcData.getEPC().toString();
            }
        } else {
            logger.error("Could not find EPC in Tag Report");
            System.exit(1);
        }

        // all of these values are optional, so check their non-nullness first
        if(tr.getAntennaID() != null) {
            antenna = tr.getAntennaID().getAntennaID().toString();
            currentAntennaID = tr.getAntennaID().getAntennaID();
        }

        if(tr.getChannelIndex() != null) {
            channel = tr.getChannelIndex().getChannelIndex().toString();
            currentChannelIndex = tr.getChannelIndex().getChannelIndex();
        }

        if( tr.getFirstSeenTimestampUTC() != null) {
            firstSeen = tr.getFirstSeenTimestampUTC().getMicroseconds().toString();
            currentReadTime = tr.getFirstSeenTimestampUTC().getMicroseconds();
        }

        if(tr.getLastSeenTimestampUTC() != null) {
            lastSeen = tr.getLastSeenTimestampUTC().getMicroseconds().toString();
        }

        if(tr.getPeakRSSI() != null) {
            peakRSSI = tr.getPeakRSSI().getPeakRSSI().toString();
        }

        if(tr.getTagSeenCount() != null) {
        	seenCount = tr.getTagSeenCount().getTagCount().toString();
        }

        List<Custom> clist = tr.getCustomList();

        for (Custom cd : clist) {
            if (cd.getClass() == ImpinjRFPhaseAngle.class) {
                currentRfPhase = ((ImpinjRFPhaseAngle) cd).getPhaseAngle().toInteger();
                phaseAngle = Integer.parseInt(((ImpinjRFPhaseAngle) cd).getPhaseAngle().toString());
            }
//            if(cd.getClass() == ImpinjPeakRSSI.class) {
//                epcString += " ImpinjPeakRSSI: " +
//                        ((ImpinjPeakRSSI) cd).getRSSI().toString();
//            }

        }

        velocity = calculateVelocity();

        di.updateReport(EPC, antenna, channel, firstSeen, lastSeen, peakRSSI, seenCount, phaseAngle, velocity);

        //logger.debug(output);


    }

    String calculateVelocity()
    {
        String out = "0.0";
        double velocity = 0;

        /* you have to have two samples from the same EPC on the same
         * antenna and channel.  NOTE: this is just a simple example.
         * More sophisticated apps would create a database with
         * this information per-EPC */
        if ((lastEPCData != null) &&
            (lastEPCData.equals(currentEPCData)) &&
            (lastAntennaID.equals(currentAntennaID)) &&
            (lastChannelIndex.equals(currentChannelIndex)) &&
            (lastReadTime.toLong() < currentReadTime.toLong()))
        {
            /* positive velocity is moving towards the antenna */
            double phaseChangeDegrees = (((double) currentRfPhase - (double) lastRfPhase)*360.0)/4096.0;
            double timeChangeUsec = (currentReadTime.intValue() - lastReadTime.intValue());

            /* always wrap the phase to between -180 and 180 */
            while( phaseChangeDegrees < -180)
                phaseChangeDegrees += 360;
            while( phaseChangeDegrees > 180)
                phaseChangeDegrees -= 360;

            /* if our phase changes close to 180 degrees, you can see we
            ** have an ambiguity of whether the phase advanced or retarded by
            ** 180 degrees (or slightly over). There is no way to tell unless
            ** you use more advanced techiques with multiple channels.  So just
            ** ignore any samples where phase change is > 90 */
            if (Math.abs((int)phaseChangeDegrees) <= 90)
            {
                /* We can divide these two to get degrees/usec, but it would be more
                ** convenient to have this in a common unit like meters/second.
                ** Here's a straightforward conversion.  NOTE: to be exact here, we
                ** should use the channel index to find the channel frequency/wavelength.
                ** For now, I'll just assume the wavelength corresponds to mid-band at
                ** 0.32786885245901635 meters. The formula below eports meters per second.
                ** Note that 360 degrees equals only 1/2 a wavelength of motion because
                ** we are computing the round trip phase change.
                **
                **  phaseChange (degrees)   1/2 wavelength     0.327 meter      1000000 usec
                **  --------------------- * -------------- * ---------------- * ------------
                **  timeChange (usec)       360 degrees       1  wavelength      1 second
                **
                ** which should net out to estimated tag velocity in meters/second */

                velocity = ((phaseChangeDegrees * 0.5 * 0.327868852 * 1000000) / (360 * timeChangeUsec));

                out = Double.toString(velocity);
            }
        }

        // save the current sample as the last sample
        lastReadTime = currentReadTime;
        lastEPCData = currentEPCData;
        lastRfPhase = currentRfPhase;
        lastAntennaID = currentAntennaID;
        lastChannelIndex = currentChannelIndex;
        return out;
    }

    // messageReceived method is called whenever a message is received
    // asynchronously on the LLRP connection.
    public void messageReceived(LLRPMessage message) {
        // convert all messages received to LTK-XML representation
        // and print them to the console

        logger.debug("Received " + message.getName() + " message asychronously");

        if (message.getTypeNum() == RO_ACCESS_REPORT.TYPENUM) {
            RO_ACCESS_REPORT report = (RO_ACCESS_REPORT) message;

            List<TagReportData> tdlist = report.getTagReportDataList();

            for (TagReportData tr : tdlist) {
                logOneTagReport(tr);
            }

            List<Custom> clist = report.getCustomList();
            for (Custom cust : clist) {
                logOneCustom(cust);
            }
            

        } else if (message.getTypeNum() == READER_EVENT_NOTIFICATION.TYPENUM) {
            // TODO 
        }
    }

    public void errorOccured(String s) {
        logger.error(s);
    }
    
    /**
     * @param args
     */
    public static void main(String[] args) {
        BasicConfigurator.configure();

        // Only show root events from the base logger
        Logger.getRootLogger().setLevel(Level.ERROR);
        DataCollector example = new DataCollector();
        logger.setLevel(Level.INFO);

        if  (args.length < 1) {
            System.out.print("Must pass reader hostname or IP as agument 1");
            System.exit(-1);
        }

        example.connect(args[0]);
        example.enableImpinjExtensions();
        example.factoryDefault();
        example.getReaderCapabilities();
        example.getReaderConfiguration();
        example.setReaderConfiguration();
        example.addRoSpec(true);
        example.enable();
        
		// Get label for activity
		Scanner reader = new Scanner(System.in);
		System.out.println("[DATA_COLLECTOR][MAIN] Enter a label for this activity: ");
		String label = reader.next();
		di.init(di, label);
		reader.close();
        
        example.start();
        for(int i = 0; i < numSnapshots; i++) {
            try {
            	// Collect samples for n milliseconds
                Thread.sleep(sleepTime);
                
                // Get snapshot
                HashMap<String, ReportData> snapshot = di.getSnapshot();
                
                // Submit snapshot
                di.submitSnapshot(snapshot);
            } catch (InterruptedException ex) {
                logger.error("Sleep Interrupted");
                example.stop();
                example.disconnect();
            }
        }
        example.stop();
        example.disconnect();
        
        System.exit(0);
    }
}

/*
 * 
 * CLASS: DataInterface
 * 
 */
class DataInterface {

	HashMap<String, ReportData> map = new HashMap<String, ReportData>();
	HashMap<String, int[]> tags = new HashMap<String, int[]>();
	
	long startTime;
	long snapshotTimestamp;
	static String activityLabel;
	
	public void loadTags() throws IOException {
	    String filePath = "tags.txt";

	    String line;
	    BufferedReader reader = new BufferedReader(new FileReader(filePath));
	    while ((line = reader.readLine()) != null) {
	        String[] parts = line.split(":", 3);
	        if (parts.length >= 1) {
	        	String key = parts[0];
	        	
	        	int[] antennas = new int[2];
	        	
	        	if (parts.length == 1) {
		        	antennas[0] = 0;
		        	antennas[1] = 0;
		            tags.put(key, antennas);	
	        	}
	        	else if (parts.length == 3) {
		        	antennas[0] = Integer.parseInt(parts[1]);
		        	antennas[1] = Integer.parseInt(parts[2]);
		            tags.put(key, antennas);	
	        	}
	        }
	        else {
	            System.out.println("[DATA_INTERFACE][loadTags] ignoring line: " + line);
	        }
	    }

	    for (String key : tags.keySet()) {
	        System.out.println(key + ":" + tags.get(key));
	    }
	    reader.close();
	}
	
	public void initMap() {		
	    for (Map.Entry<String, int[]> entry : tags.entrySet()) {
	        String key = entry.getKey();
	        
	        ReportData report = new ReportData(key, "0", "0", "0000", "0000", "0", "0", 0, "0");
	        map.put(key, report);
	    }
	}
	
	public void printMap() {
	    Iterator it = tags.entrySet().iterator();
	    while (it.hasNext()) {
	        Map.Entry pair = (Map.Entry)it.next();
	        System.out.println(pair.getKey() + " = " + pair.getValue());
	        it.remove();
	    }
	}
	
	public void retrieveReport(String EPC) {
		ReportData rd = map.get(EPC);
		rd.printData();
	}
	
	public void updateReport(String EPC, String antenna, String channel, String firstSeen, String lastSeen,
			String peakRSSI, String seenCount, int phaseAngle, String velocity) {
		
		if(tags.get(EPC) != null) {
			int updatingAntenna = Integer.parseInt(antenna);
			int assignedAntennas[] = tags.get(EPC);
			if ((updatingAntenna != assignedAntennas[0] && updatingAntenna != assignedAntennas[1]) && assignedAntennas[0] != 0 ) {
				System.out.println("[DATA_INTERFACE][updateReport] Cannot update tag " + EPC + " with antenna " + updatingAntenna + ", must use antenna "
						+ assignedAntennas[0] + " or " + assignedAntennas[1] + ".");
			}
			else {
				System.out.print("[DATA_INTERFACE][updateReport] Updating tag " + EPC + "...");
				ReportData rd = new ReportData(EPC, antenna, channel, firstSeen, lastSeen, peakRSSI, seenCount, phaseAngle, velocity);
				rd.updateLastUpdated();
				map.put(EPC, rd);
				System.out.println("[DONE]");
			}
		}
		else {
			System.out.println("[DATA_INTERFACE][updateReport] Cannot update tag " + EPC + ". Tag not in dictionary.");
		}
	}
	
	public HashMap<String, ReportData> getSnapshot() {
		System.out.print("[DATA_INTERFACE][getSnapshot] Generating snapshot of tag reports...");
		
		Timestamp timestamp = new Timestamp(System.currentTimeMillis());
		long ts = timestamp.getTime();
		snapshotTimestamp = ts;
		
		HashMap<String, ReportData> snapshot = new HashMap<String, ReportData>();
		
	    for (Map.Entry<String, ReportData> entry : map.entrySet()) {
	        String key = entry.getKey();
	        ReportData rd = entry.getValue();
	        
	        System.out.println("ts: " + ts);
	        System.out.println("rd LastUpdated: " + rd.getLastUpdated());
	        
	        if ((ts - rd.getLastUpdated()) > 20000) {
	        	System.out.println("Timestamp invalid.");
	        	rd = new ReportData(rd.getEPC(), "0", "0", "0000", "0000", "0", "0", 0, "0");
	        	snapshot.put(key, rd);
	        }
	        else {
	        	snapshot.put(key, rd);
	        }
	    }
	    
	    System.out.println("[DONE]");
	    
	    return snapshot;
	}
	
	public void printSnapshot(HashMap<String, ReportData> hm) {
	    Iterator it = hm.entrySet().iterator();
	    while (it.hasNext()) {
	        Map.Entry pair = (Map.Entry)it.next();
	        ReportData rd = hm.get(pair.getKey());
	        if (rd.getAntenna() == "0") {
	        	System.out.println("[DATA_INTERFACE][printSnapshot] " + pair.getKey() + " = OUTDATED REPORT");
	        }
	        else {
	        	System.out.println("[DATA_INTERFACE][printSnapshot] " + pair.getKey() + " = " + pair.getValue());
	        }
	        it.remove();
	    }
	}
	
	public void submitSnapshot(HashMap<String, ReportData> hm) {
		System.out.println("[DATA_INTERFACE][submitSnapshot] Submitting snapshot to MongoDB...");
		
//		MongoClient mongoClient = new MongoClient(new MongoClientURI("mongodb://localhost:27017")); // For remote server
		MongoClient mongoClient = new MongoClient(); // For local server
		
		DBObject snapshot = new BasicDBObject("_id", snapshotTimestamp);
		
		Timestamp timestamp = new Timestamp(System.currentTimeMillis());
		long elapsedTime = timestamp.getTime() - startTime;
		
		snapshot.put("activity_label", activityLabel);
		snapshot.put("elapsed_time", elapsedTime);
		
		List<BasicDBObject> tagArray = new ArrayList<>();
		
	    for (Map.Entry<String, ReportData> entry : hm.entrySet()) {
	        String key = entry.getKey();
	        ReportData rd = entry.getValue();
	        
	        tagArray.add(new BasicDBObject("_id", rd.getEPC())
	        		.append("lastUpdated", rd.getLastUpdated())
	        		.append("antenna", rd.getAntenna())
	        		.append("channel", rd.getChannel())
	        		.append("firstSeen", rd.getFirstSeen())
	        		.append("lastSeen", rd.getLastSeen())
	        		.append("peakRSSI", rd.getPeakRSSI())
	        		.append("seenCount", rd.getSeenCount())
	        		.append("phaseAngle", rd.getPhaseAngle())
	        		.append("velocity", rd.getVelocity()));
	    }
	    
	    snapshot.put("tags", tagArray);
	    
		DB database = mongoClient.getDB("RALT_RFID_HAR_System");
		DBCollection collection = database.getCollection(activityLabel);
		
		collection.insert(snapshot);
		
		mongoClient.close();
		
		System.out.println("[DONE]");
	}
	
	public void init(DataInterface di, String label) {
		// Load tags: EPC and assigned antenna
		System.out.println("[DATA_INTERFACE][INIT] Loading tags...");
		try {
			di.loadTags();
		} catch (IOException e1) {
			e1.printStackTrace();
		}
		System.out.println("[DATA_INTERFACE][INIT] Loading tags...[DONE]");
		
		// Initialise HashMap of tag reports
		System.out.print("[DATA_INTERFACE][INIT] Initialising HashMap of tag reports...");
		di.initMap();
		System.out.println("[DONE]");
		
		// Load tags: EPC and assigned antenna
		System.out.println("[DATA_INTERFACE][INIT] Loading tags...");
		try {
			di.loadTags();
		} catch (IOException e1) {
			e1.printStackTrace();
		}
		System.out.println("[DATA_INTERFACE][INIT] Loading tags...[DONE]");
		
		// Initialise HashMap of tag reports
		System.out.print("[DATA_INTERFACE][INIT] Initialising HashMap of tag reports...");
		di.initMap();
		System.out.println("[DONE]");
		
		// Set label for activity
		activityLabel = label;
		
		// Record start time
		Timestamp timestamp = new Timestamp(System.currentTimeMillis());
		startTime = timestamp.getTime();
	}
	
}

/*
 * 
 * CLASS: ReportData
 * 
 */
class ReportData {
	
  String EPC;
  long lastUpdated;
	
  String antenna;
  String channel;
  String firstSeen;
  String lastSeen;
  String peakRSSI;
  String seenCount;
  int phaseAngle;
  String velocity;
  
  public ReportData(String EPC, String antenna, String channel, String firstSeen, String lastSeen,
  					String peakRSSI, String seenCount, int phaseAngle, String velocity) {
  	
  	Timestamp timestamp = new Timestamp(System.currentTimeMillis());
  	
  	this.EPC = EPC;
  	this.lastUpdated = timestamp.getTime();
  	this.antenna = antenna;
  	this.channel = channel;
  	this.firstSeen = firstSeen;
  	this.lastSeen = lastSeen;
  	this.peakRSSI = peakRSSI;
  	this.seenCount = seenCount;
  	this.phaseAngle = phaseAngle;
  	this.velocity = velocity;
  }
  
  public String getEPC() {
  	return this.EPC;
  }
 
  public long getLastUpdated() {
  	return this.lastUpdated;
  }
  
  public String getAntenna() {
  	return this.antenna;
  }
  
  public String getChannel() {
  	return this.channel;
  }

  public String getFirstSeen() {
  	return this.firstSeen;
  }
  
  public String getLastSeen() {
  	return this.lastSeen;
  }
  
  public String getPeakRSSI() {
  	return this.peakRSSI;
  }
  
  public String getSeenCount() {
  	return this.seenCount;
  }
  
  public int getPhaseAngle() {
  	return this.phaseAngle;
  }
  
  public String getVelocity() {
  	return this.velocity;
  }
  
  public void printData() {
  	System.out.println("[DATA_INTERFACE][REPORT_DATA] EPC: " + this.EPC);
  	System.out.println("[DATA_INTERFACE][REPORT_DATA] Timestamp: " + this.lastUpdated);
  }
  
  public void updateLastUpdated() {
	  Timestamp timestamp = new Timestamp(System.currentTimeMillis());
	  this.lastUpdated = timestamp.getTime();
  }
  
} 