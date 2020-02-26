package smos.application.addressManagement;

import java.io.IOException;
import java.sql.SQLException;

import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpSession;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import smos.Environment;
import smos.bean.User;
import smos.bean.Address;
import smos.exception.DuplicatedEntityException;
import smos.exception.EntityNotFoundException;
import smos.exception.InvalidValueException;
import smos.exception.MandatoryFieldException;
import smos.storage.ManagerAddress;
import smos.storage.ManagerUser;
import smos.storage.connectionManagement.exception.ConnectionException;

/**
 * Servlet utilizzata per inserire un indirizzo nel database
 * 
 * @author Vecchione Giuseppe
 */
public class ServletInsertAddress extends HttpServlet {

	private static final long serialVersionUID = 8318905833953187814L;
	
	/**
	 * Definizione del metodo doGet
	 * 
	 * @param pRequest
	 * 
	 * @param pResponse
	 * 
	 */
	
	public void doGet(HttpServletRequest pRequest, HttpServletResponse pResponse){
		String gotoPage="./showAddressList";
		String errorMessage="";
		HttpSession session = pRequest.getSession();
		ManagerUser managerUser= ManagerUser.getInstance();
		ManagerAddress managerAddress= ManagerAddress.getInstance();
		User loggedUser = (User) session.getAttribute("loggedUser");
		try {
				if(loggedUser==null){
					pResponse.sendRedirect("./index.htm");
					return;
				}
				if(!managerUser.isAdministrator(loggedUser)){
					errorMessage= "L' utente collegato non ha accesso alla funzionalita'!";
					gotoPage="./error.jsp";
				}
				
				Address address= new Address();
				address.setName(pRequest.getParameter("name"));
				
				/**
				 * Verifichiamo che l' indirizzo non sia presente nel database
				 * e lo inseriamo
				 */
				if(!managerAddress.exists(address)){
					managerAddress.insert(address);
				}else{
					throw new DuplicatedEntityException("Indirizzo gia' esistente");
				}
				
			} catch (IOException ioException) {
				errorMessage = Environment.DEFAULT_ERROR_MESSAGE + ioException.getMessage();
				gotoPage = "./error.jsp";
				ioException.printStackTrace();
			} catch (SQLException sqlException) {
				errorMessage =  Environment.DEFAULT_ERROR_MESSAGE + sqlException.getMessage();
				gotoPage = "./error.jsp";
				sqlException.printStackTrace();
			} catch (EntityNotFoundException entityNotFoundException) {
				errorMessage =  Environment.DEFAULT_ERROR_MESSAGE + entityNotFoundException.getMessage();
				gotoPage = "./error.jsp";
				entityNotFoundException.printStackTrace();
			} catch (ConnectionException connectionException) {
				errorMessage =  Environment.DEFAULT_ERROR_MESSAGE + connectionException.getMessage();
				gotoPage = "./error.jsp";
				connectionException.printStackTrace();
			} catch (MandatoryFieldException mandatoryFieldException) {
				errorMessage =  Environment.DEFAULT_ERROR_MESSAGE + mandatoryFieldException.getMessage();
				gotoPage = "./error.jsp";
				mandatoryFieldException.printStackTrace();
			} catch (InvalidValueException invalidValueException) {
				errorMessage =  Environment.DEFAULT_ERROR_MESSAGE + invalidValueException.getMessage();
				gotoPage = "./error.jsp";
				invalidValueException.printStackTrace();
			} catch (DuplicatedEntityException duplicatedEntityException) {
				errorMessage =  Environment.DEFAULT_ERROR_MESSAGE + duplicatedEntityException.getMessage();
				gotoPage = "./error.jsp";
				duplicatedEntityException.printStackTrace();
			}
			session.setAttribute("errorMessage", errorMessage);
			try {
				pResponse.sendRedirect(gotoPage);
			} catch (IOException ioException) {
				errorMessage = Environment.DEFAULT_ERROR_MESSAGE + ioException.getMessage();
				gotoPage = "./error.jsp";
				ioException.printStackTrace();
			}
		}
	
	
	/**
	 * Definizione del metodo doPost
	 * 
	 * @param pRequest
	 * @param pResponse
	 * 
	 */
	
	protected void doPost(HttpServletRequest pRequest, 
			HttpServletResponse pResponse) {
		this.doGet(pRequest, pResponse);
	}
	

}
