//package org.impinj.llrp.ltk.examples.datacollector;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.IOException;
import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.concurrent.TimeoutException;
import java.util.List;
import java.util.HashMap;

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

public class DataInterface {

	HashMap<String, ReportData> map = new HashMap<String, ReportData>();
	HashMap<String, Integer> tags = new HashMap<String, Integer>();
	
	long snapshotTimestamp;
	static String activityLabel;
	
	public void loadTags() throws IOException {
	    String filePath = "tags.txt";

	    String line;
	    BufferedReader reader = new BufferedReader(new FileReader(filePath));
	    while ((line = reader.readLine()) != null) {
	        String[] parts = line.split(":", 2);
	        if (parts.length >= 2) {
	        	int atnenna = Integer.parseInt(parts[1]);
	            String key = parts[0];
	            tags.put(key, atnenna);
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
	    for (Map.Entry<String, Integer> entry : tags.entrySet()) {
	        String key = entry.getKey();
	        
	        ReportData report = new ReportData(key, "1", "1", "0000", "1111", "50", "10", 5, "3");
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
			int assignedAntenna = tags.get(EPC);
			if (updatingAntenna != assignedAntenna) {
				System.out.println("[DATA_INTERFACE][updateReport] Cannot update tag " + EPC + " with antenna " + updatingAntenna + ", must use antenna "
						+ assignedAntenna + ".");
			}
			else {
				System.out.print("[DATA_INTERFACE][updateReport] Updating tag " + EPC + "...");
				ReportData rd = new ReportData(EPC, antenna, channel, firstSeen, lastSeen, peakRSSI, seenCount, phaseAngle, velocity);
				map.put("EPC", rd);
				System.out.println("[DONE]");
			}
		}
		else {
			System.out.println("[DATA_INTERFACE][updateReport] Cannot update tag " + EPC + ". Tag not in dictionary.");
		}
	}
	
	public HashMap<String, ReportData> getSnapshot() {		
		Timestamp timestamp = new Timestamp(System.currentTimeMillis());
		long ts = timestamp.getTime();
		snapshotTimestamp = ts;
		
		HashMap<String, ReportData> snapshot = new HashMap<String, ReportData>();
		
	    for (Map.Entry<String, ReportData> entry : map.entrySet()) {
	        String key = entry.getKey();
	        ReportData rd = entry.getValue();
	        
	        if ((ts - rd.getLastUpdated()) > 4999) {
	        	rd = new ReportData(rd.getEPC(), "0", "0", "0000", "0000", "0", "0", 0, "0");
	        	snapshot.put(key, rd);
	        }
	        else {
	        	snapshot.put(key, rd);
	        }
	    }
	    
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
//		MongoClient mongoClient = new MongoClient(new MongoClientURI("mongodb://localhost:27017")); // For remote server
		MongoClient mongoClient = new MongoClient(); // For local server
		
		DBObject snapshot = new BasicDBObject("_id", snapshotTimestamp);
		
		snapshot.put("activityLabel", activityLabel);
		
	    for (Map.Entry<String, ReportData> entry : hm.entrySet()) {
	        String key = entry.getKey();
	        ReportData rd = entry.getValue();
	        
	        DBObject report = new BasicDBObject("_id", rd.getEPC())
	        		.append("lastUpdated", rd.getLastUpdated())
	        		.append("antenna", rd.getAntenna())
	        		.append("channel", rd.getChannel())
	        		.append("firstSeen", rd.getFirstSeen())
	        		.append("lastSeen", rd.getLastSeen())
	        		.append("peakRSSI", rd.getPeakRSSI())
	        		.append("seenCount", rd.getSeenCount())
	        		.append("phaseAngle", rd.getPhaseAngle())
	        		.append("velocity", rd.getVelocity());
	        snapshot.put(rd.getEPC(), report);
	    }
	    
		DB database = mongoClient.getDB("RALT_RFID_HAR_System");
		DBCollection collection = database.getCollection(activityLabel);
		
		collection.insert(snapshot);
		
		mongoClient.close();
	}
	
	public static void main(String[] args) {
		// Instantiate class
		DataInterface di = new DataInterface();
				
		// Load tags: EPC and assigned antenna
		System.out.println("[DATA_INTERFACE][MAIN] Loading tags...");
		try {
			di.loadTags();
		} catch (IOException e1) {
			e1.printStackTrace();
		}
		System.out.println("[DATA_INTERFACE][MAIN] Loading tags...[DONE]");
		
		// Initialise HashMap of tag reports
		System.out.print("[DATA_INTERFACE][MAIN] Initialising HashMap of tag reports...");
		di.initMap();
		System.out.println("[DONE]");
		
		// Get label for activity
		Scanner reader = new Scanner(System.in);
		System.out.println("[DATA_INTERFACE][MAIN] Enter a label for this activity: ");
		String label = reader.next();
		activityLabel = label;
		reader.close();
		
		// Test updating of tag
		System.out.println("[DATA_INTERFACE][MAIN] Updating a tag that does not exist (300833B2DDD90140000000XX)...");
		di.updateReport("300833B2DDD90140000000XX", "1", "1", "0000", "1234", "50", "10", 5, "3");
		System.out.println("[DATA_INTERFACE][MAIN] Attempting to update tag report for 300833B2DDD90140000000F0 with INCORRECT antenna...");
		di.updateReport("300833B2DDD90140000000F0", "1", "1", "0000", "1234", "50", "10", 5, "3");
		System.out.println("[DATA_INTERFACE][MAIN] Attempting to update tag report for 300833B2DDD90140000000F0 with CORRECT antenna...");
		di.updateReport("300833B2DDD90140000000F0", "2", "1", "0000", "1234", "50", "10", 5, "3");
		
		while(true) {
			// Get snapshot of tag reports
			System.out.print("[DATA_INTERFACE][MAIN] Generating snapshot of tag reports...");
			HashMap<String, ReportData> snapshot = di.getSnapshot();
			System.out.println("[DONE]");
			
			// Submit snapshot to MongoDB
			System.out.println("[DATA_INTERFACE][MAIN] Submitting snapshot to MongoDB...");
			di.submitSnapshot(snapshot);
			System.out.println("[DATA_INTERFACE][MAIN] Submitting snapshot to MongoDB... [DONE]");
			
			try {
				TimeUnit.MILLISECONDS.sleep(4000);
			} catch (InterruptedException e) {
				e.printStackTrace();
			}
		}
	}
	
}

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
    
} 