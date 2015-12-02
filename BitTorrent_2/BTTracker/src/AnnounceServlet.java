

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.BufferedWriter;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.PrintWriter;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.security.MessageDigest;

import javax.servlet.ServletException;
import javax.servlet.ServletOutputStream;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import com.mysql.jdbc.PreparedStatement;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.logging.Level;
import java.util.logging.Logger;

/**
 * Servlet implementation class UpdateServlet
 */
public class AnnounceServlet extends HttpServlet {
	private static final long serialVersionUID = 1L;
       
    /**
     * @see HttpServlet#HttpServlet()
     */
    public AnnounceServlet() {
        super();
        // TODO Auto-generated constructor stub
    }

	/**
	 * @see HttpServlet#doGet(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
		response.getWriter().append("Served at: ").append(request.getContextPath());
	}

	/**
	 * @see HttpServlet#doPost(HttpServletRequest request, HttpServletResponse response)
	 */
	protected void doPost(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// TODO Auto-generated method stub
	    String command = request.getParameter("command");
	    response.setContentType("text/html");
        PrintWriter out = response.getWriter();
        String basePath = "/Users/shamikulamin/Documents/tracker files";
    	if(command.equalsIgnoreCase("list")){
    		try{
    			File[] fileList=getList(basePath);
    			for (int i = 1; i < fileList.length; i++) {
    				BufferedReader in = new BufferedReader(new FileReader(fileList[i]));
    				String str="";
    				for(int w=0;w<4;w++){
    					if(w!=2){
    						String result = in.readLine().split(":")[1];
    						str=str+result;
    					}	
    				}
    				System.out.println(str);
    				out.println(str);
    				in.close();
    			}
    		}
    		catch(Exception e){
    			System.out.println(e);
    		
    		}
    	}
    	else if(command.equalsIgnoreCase("get")){
    	    String filename = request.getParameter("filenametrack");
    	    String contents = readFile(basePath+"/"+filename);
    	    out.println(contents);
    	}
    	else if(command.equalsIgnoreCase("createtracker")){
    		System.out.println("creating.....");
    		String filename = request.getParameter("filename");
    		String filesize = request.getParameter("filesize");
    		String desc = request.getParameter("description");
    		String md5 = request.getParameter("md5");
    		String ip = request.getParameter("ip");
    		String port = request.getParameter("port");
    		String timeStamp = new SimpleDateFormat("yyyy.MM.dd.HH.mm.ss").format(new Date());
    		try{
    			PrintWriter writer = new PrintWriter(basePath+"/"+filename, "UTF-8");
	    		writer.println("File Name: "+filename);
	    		writer.println("File Size: "+filesize);
	    		writer.println("Description: "+desc);
	    		writer.println("MD5: "+md5);
	    		writer.println(ip+":"+port+":"+"0:"+filesize+":"+timeStamp);
	    		writer.close();
	    		out.println("Create Tracker Successful");
    		}
    		catch(Exception e){
    			System.out.println(e);
    			out.println("Create Tracker Failure");
    		}
    		
    		
    	}
    	else if(command.equalsIgnoreCase("updatetracker")){
	    	String filename = request.getParameter("filename");
	    	String sbyte = request.getParameter("sbyte");
	    	String ebyte = request.getParameter("ebyte");
	    	String ip = request.getParameter("ip");
	    	String port = request.getParameter("port");
	    	String file = basePath+"/"+filename;
	    	try{
	    		BufferedWriter out1 = new BufferedWriter (new FileWriter(file,true));
	    		out1.write("\n"+ip+":"+port+":"+sbyte+":"+ebyte);
	    		out1.close();
	    		out.println("Update Tracker Successful");
    		}
    		catch(Exception e){
    			System.out.println(e);
    		}
    	}
    	else{
    		out.println("Invalid Command");
    	}
	   // out.close();
	        
	  }
	String readFile(String fileName) throws IOException {
	    BufferedReader br = new BufferedReader(new FileReader(fileName));
	    try {
	        StringBuilder sb = new StringBuilder();
	        String line = br.readLine();

	        while (line != null) {
	            sb.append(line);
	            sb.append("\n");
	            line = br.readLine();
	        }
	        return sb.toString();
	    } 
	    catch(Exception e){
	    	System.out.println(e);
	    	return e.toString();
	    }
	    finally {
	        br.close();
	    }
	}
  File[] getList(String path) throws IOException{
	  File folder = new File(path);
	  File[] listOfFiles = folder.listFiles();
	  return listOfFiles;
  }
  private static String getMD5(File file, String algorithm){
	    try (FileInputStream inputStream = new FileInputStream(file)) {
	        MessageDigest digest = MessageDigest.getInstance(algorithm);
	 
	        byte[] bytesBuffer = new byte[1024];
	        int bytesRead = -1;
	 
	        while ((bytesRead = inputStream.read(bytesBuffer)) != -1) {
	            digest.update(bytesBuffer, 0, bytesRead);
	        }
	 
	        byte[] hashedBytes = digest.digest();
	        char[] hexArray = "0123456789ABCDEF".toCharArray();
	        char[] hexChars = new char[hashedBytes.length * 2];
	        for ( int j = 0; j < hashedBytes.length; j++ ) {
	            int v = hashedBytes[j] & 0xFF;
	            hexChars[j * 2] = hexArray[v >>> 4];
	            hexChars[j * 2 + 1] = hexArray[v & 0x0F];
	        }
	 
	        return new String(hexChars);
	    } catch (Exception ex) {
	        
	    }
	    return null;
  }
}
