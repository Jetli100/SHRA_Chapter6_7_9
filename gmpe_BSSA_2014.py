# Note: The codes were originally created by Prof. Jack Baker
import numpy as np
import math
import os
import scipy.io as sio
from scipy.stats import norm
from scipy.interpolate import interp1d
import ast

# BSSA14 NGA-West2 model, based on teh following citation

# Boore, D. M., Stewart, J. P., Seyhan, E., and Atkinson, G. M. (2014). 
# NGA-West2 Equations for Predicting PGA, PGV, and 5% Damped PSA for 
# Shallow Crustal Earthquakes. Earthquake Spectra, 30(3), 1057 1085.
# http://www.earthquakespectra.org/doi/abs/10.1193/070113EQS184M

# Provides ground-mtion prediction equations for computing medians and
# standard devisations of average horizontal component internsity measures
# (IMs) for shallow crustal earthquakes in active tectonic regions.

##############
### Inputs ###
##############

# M     = Moment Magnitude
# T     = Period (sec); Use Period = -1 for PGV computation
#                 Use 1000 for output the array of Sa with original period
#                 (no interpolation)
# Rjb   = Joyner-Boore distance (km)
# Fault_Type    = 0 for unspecified fault
#               = 1 for strike-slip fault
#               = 2 for normal fault
#               = 3 for reverse fault
# region        = 0 for global (incl. Taiwan)
#               = 1 for California
#               = 2 for Japan
#               = 3 for China or Turkey
#               = 4 for Italy 
# z1            = Basin depth (km); depth from the groundsurface to the
#                 1km/s shear-wave horizon.
#               = 999 if unknown
# Vs30          = shear wave velocity averaged over top 30 m in m/s


###############
### Outputs ###
###############

# median        = Median amplitude prediction
# sigma         = NATURAL LOG standard deviation


def BSSA_2014_sub(M, ip, Rjb, U, SS, NS, RS, region, z1, Vs30):
#     Coefficients
    mref=4.5;
    rref=1;
    v_ref=760; 
    f1=0;
    f3=0.1;
    v1=225;
    v2=300;
    period = [-1, 0, 0.01, 0.02, 0.03, 0.05, 0.075, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.75, 1, 1.5, 2, 3, 4, 5, 7.5, 10]
    mh=[6.2, 5.5, 5.5, 5.5, 5.5, 5.5, 5.5, 5.54, 5.74, 5.92, 6.05, 6.14, 6.2, 6.2, 6.2, 6.2, 6.2, 6.2, 6.2, 6.2, 6.2, 6.2, 6.2]
    e0="[5.037	0.4473	0.4534	0.48598	0.56916	0.75436	0.96447	1.1268	1.3095	1.3255	1.2766	1.2217	1.1046	0.96991	0.66903	0.3932	-0.14954	-0.58669	-1.1898	-1.6388	-1.966	-2.5865	-3.0702]"
    e1="[5.078	0.4856	0.4916	0.52359	0.6092	0.79905	1.0077	1.1669	1.3481	1.359	1.3017	1.2401	1.1214	0.99106	0.69737	0.4218	-0.11866	-0.55003	-1.142	-1.5748	-1.8882	-2.4874	-2.9537]"
    e2="[4.849	0.2459	0.2519	0.29707	0.40391	0.60652	0.77678	0.8871	1.0648	1.122	1.0828	1.0246	0.89765	0.7615	0.47523	0.207	-0.3138	-0.71466	-1.23	-1.6673	-2.0245	-2.8176	-3.3776]"
    e3="[5.033	0.4539	0.4599	0.48875	0.55783	0.72726	0.9563	1.1454	1.3324	1.3414	1.3052	1.2653	1.1552	1.012	0.69173	0.4124	-0.1437	-0.60658	-1.2664	-1.7516	-2.0928	-2.6854	-3.1726]"
    e4="[1.073	1.431	1.421	1.4331	1.4261	1.3974	1.4174	1.4293	1.2844	1.1349	1.0166	0.95676	0.96766	1.0384	1.2871	1.5004	1.7622	1.9152	2.1323	2.204	2.2299	2.1187	1.8837]"
    e5="[-0.1536	0.05053	0.04932	0.053388	0.061444	0.067357	0.073549	0.055231	-0.042065	-0.11096	-0.16213	-0.1959	-0.22608	-0.23522	-0.21591	-0.18983	-0.1467	-0.11237	-0.04332	-0.014642	-0.014855	-0.081606	-0.15096 ]"
    e6="[0.2252	-0.1662	-0.1659	-0.16561	-0.1669	-0.18082	-0.19665	-0.19838	-0.18234	-0.15852	-0.12784	-0.092855	-0.023189	0.029119	0.10829	0.17895	0.33896	0.44788	0.62694	0.76303	0.87314	1.0121	1.0651]"
    c1="[-1.24300	-1.13400	-1.13400	-1.13940	-1.14210	-1.11590	-1.08310	-1.06520	-1.05320	-1.06070	-1.07730	-1.09480	-1.12430	-1.14590	-1.17770	-1.19300	-1.20630	-1.21590	-1.21790	-1.21620	-1.21890	-1.25430	-1.32530]"
    c2="[0.14890	0.19170	0.19160	0.18962	0.18842	0.18709	0.18225	0.17203	0.15401	0.14489	0.13925	0.13388	0.12512	0.12015	0.11054	0.10248	0.09645	0.09636	0.09764	0.10218	0.10353	0.12507	0.15183]"
    c3="[-0.00344	-0.00809	-0.00809	-0.00807	-0.00834	-0.00982	-0.01058	-0.01020	-0.00898	-0.00772	-0.00652	-0.00548	-0.00405	-0.00322	-0.00193	-0.00121	-0.00037	0.00000	0.00000	-0.00005	0.00000	0.00000	0.00000]"
    h="[5.3	4.5	4.5	4.5	4.49	4.2	4.04	4.13	4.39	4.61	4.78	4.93	5.16	5.34	5.6	5.74	6.18	6.54	6.93	7.32	7.78	9.48	9.66]"

    deltac3_gloCATW="[0.000000	0.000000	0.000000	0.000000	0.000000	0.000000	0.000000	0.000000	0.000000	0.000000	0.000000	0.000000	0.000000	0.000000	0.000000	0.000000	0.000000	0.000000	0.000000	0.000000	0.000000	0.000000	0.000000]"
    deltac3_CHTU="[0.004350	0.002860	0.002820	0.002780	0.002760	0.002960	0.002960	0.002880	0.002790	0.002610	0.002440	0.002200	0.002110	0.002350	0.002690	0.002920	0.003040	0.002920	0.002620	0.002610	0.002600	0.002600	0.003030]"
    deltac3_ITJA="[-0.000330	-0.002550	-0.002440	-0.002340	-0.002170	-0.001990	-0.002160	-0.002440	-0.002710	-0.002970	-0.003140	-0.003300	-0.003210	-0.002910	-0.002530	-0.002090	-0.001520	-0.001170	-0.001190	-0.001080	-0.000570	0.000380	0.001490]"

    c="[-0.8400	-0.6000	-0.6037	-0.5739	-0.5341	-0.4580	-0.4441	-0.4872	-0.5796	-0.6876	-0.7718	-0.8417	-0.9109	-0.9693	-1.0154	-1.0500	-1.0454	-1.0392	-1.0112	-0.9694	-0.9195	-0.7766	-0.6558]"
    vc="[1300.00	1500.00	1500.20	1500.36	1502.95	1501.42	1494.00	1479.12	1442.85	1392.61	1356.21	1308.47	1252.66	1203.91	1147.59	1109.95	1072.39	1009.49	922.43	844.48	793.13	771.01	775.00]"
    f4="[-0.1000	-0.1500	-0.1483	-0.1471	-0.1549	-0.1963	-0.2287	-0.2492	-0.2571	-0.2466	-0.2357	-0.2191	-0.1958	-0.1704	-0.1387	-0.1052	-0.0679	-0.0361	-0.0136	-0.0032	-0.0003	-0.0001	0.0000]"
    f5="[-0.00844	-0.00701	-0.00701	-0.00728	-0.00735	-0.00647	-0.00573	-0.00560	-0.00585	-0.00614	-0.00644	-0.00670	-0.00713	-0.00744	-0.00812	-0.00844	-0.00771	-0.00479	-0.00183	-0.00152	-0.00144	-0.00137	-0.00136]"
    f6="[-9.900	-9.900	-9.9	-9.9	-9.9	-9.9	-9.9	-9.9	-9.9	-9.9	-9.9	-9.9	-9.9	-9.9	0.092	0.367	0.638	0.871	1.135	1.271	1.329	1.329	1.183]"
    f7="[-9.900	-9.900	-9.9	-9.9	-9.9	-9.9	-9.9	-9.9	-9.9	-9.9	-9.9	-9.9	-9.9	-9.9	0.059	0.208	0.309	0.382	0.516	0.629	0.738	0.809	0.703]"
    tau1="[0.4010	0.3980	0.4020	0.4090	0.4450	0.5030	0.4740	0.4150	0.3540	0.3440	0.3500	0.3630	0.3810	0.4100	0.4570	0.4980	0.5250	0.5320	0.5370	0.5430	0.5320	0.5110	0.4870]"
    tau2="[0.3460	0.3480	0.3450	0.3460	0.3640	0.4260	0.4660	0.4580	0.3880	0.3090	0.2660	0.2290	0.2100	0.2240	0.2660	0.2980	0.3150	0.3290	0.3440	0.3490	0.3350	0.2700	0.2390]"
    phi1="[0.6440	0.6950	0.6980	0.7020	0.7210	0.7530	0.7450	0.7280	0.7200	0.7110	0.6980	0.6750	0.6430	0.6150	0.5810	0.5530	0.5320	0.5260	0.5340	0.5360	0.5280	0.5120	0.5100]"
    phi2="[0.5520	0.4950	0.4990	0.5020	0.5140	0.5320	0.5420	0.5410	0.5370	0.5390	0.5470	0.5610	0.5800	0.5990	0.6220	0.6250	0.6190	0.6180	0.6190	0.6160	0.6220	0.6340	0.6040]"
    dphiR="[0.082	0.100	0.096	0.092	0.081	0.063	0.064	0.087	0.120	0.136	0.141	0.138	0.122	0.109	0.100	0.098	0.104	0.105	0.088	0.070	0.061	0.058	0.060]"
    dphiV="[0.080	0.070	0.070	0.030	0.029	0.030	0.022	0.014	0.015	0.045	0.055	0.050	0.049	0.060	0.070	0.020	0.010	0.008	0.000	0.000	0.000	0.000	0.000]"
    R1="[105.000	110.000	111.670	113.100	112.130	97.930	85.990	79.590	81.330	90.910	97.040	103.150	106.020	105.540	108.390	116.390	125.380	130.370	130.360	129.490	130.220	130.720	130.000]"
    R2="[272.000	270.000	270.000	270.000	270.000	270.000	270.040	270.090	270.160	270.000	269.450	268.590	266.540	265.000	266.510	270.000	262.410	240.140	195.000	199.450	230.000	250.390	210.000]"
    
    elements = [e0, e1, e2, e3, e4, e5, e6, c1, c2, c3, h, deltac3_gloCATW, deltac3_CHTU, deltac3_ITJA, c, vc, f4, f5, f6, f7, tau1, tau2, phi1, phi2, dphiR, dphiV, R1, R2]
    names = ["e0", "e1", "e2", "e3", "e4", "e5", "e6", "c1", "c2", "c3", "h", "deltac3_gloCATW", "deltac3_CHTU", "deltac3_ITJA", "c", "vc", "f4", "f5", "f6", "f7", "tau1", "tau2", "phi1", "phi2", "dphiR", "dphiV", "R1", "R2"]
    dict = {}
    i = 0
    for ele in elements:
        ele = ele.replace('\t', ',')
        dict[names[i]] = ast.literal_eval(ele)
        i += 1

    # The source(event function):
    if M <= mh[ip]:
        F_E = np.array(dict["e0"][ip]) * U + np.array(dict["e1"][ip]) * SS + np.array(dict["e2"][ip]) * NS + np.array(dict["e3"][ip]) * RS + np.array(dict["e4"][ip]) * (M - mh[ip]) + np.array(dict["e5"][ip]) * (M - mh[ip])**2
    else:
        F_E = np.array(dict["e0"][ip]) * U + np.array(dict["e1"][ip]) * SS + np.array(dict["e2"][ip]) * NS + np.array(dict["e3"][ip]) * RS + np.array(dict["e6"][ip]) * (M - mh[ip])
    
    # The path function:
    if (region == 0 or region == 1):
        deltac3 = dict["deltac3_gloCATW"]
    elif region == 3:
        deltac3 = dict["deltac3_CHTU"]
    elif (region == 2 or region == 4):
        deltac3 = dict["deltac3_ITJA"]

    r = np.sqrt(Rjb**2+dict["h"][ip]**2)
    F_P = (dict["c1"][ip] + dict["c2"][ip] * (M - mref)) * np.log (r / rref) + (dict["c3"][ip] + deltac3[ip]) * (r - rref)

# FIND PGAr
    if (Vs30 != v_ref or ip != 1):
        PGA_r,sigma_r = BSSA_2014_sub(M, 1, Rjb, U, SS, NS, RS, region, z1, v_ref)   

    # The site function:
    # Linear component
        if Vs30 <= dict["vc"][ip]:
            ln_Flin = dict["c"][ip] * np.log(Vs30 / v_ref)
        else:
            ln_Flin = dict["c"][ip] * np.log(dict["vc"][ip]/ v_ref)

    # Nonlinear component
        f2 = dict["f4"][ip] * (np.exp(dict["f5"][ip]*(min(Vs30,760)-360)) - np.exp(dict["f5"][ip]*(760-360)))
        ln_Fnlin = f1 + f2 * np.log((PGA_r+f3) / f3)
        
    # Effect of basin depth
        if z1 != 999:
            if region == 2:  # if in Japan
                mu_z1 = np.exp(-5.23/2 * np.log((Vs30**2 + 412.39**2) / (1360**2 + 412.39**2))) / 1000
            else:
                mu_z1 = np.exp(-7.15/4 * np.log((Vs30**4 + 570.94**4) / (1360**4 + 570.94**4))) / 1000
                
            dz1 = z1 - mu_z1
        else:
            dz1=0

        if z1 != 999:
            if period[ip] < 0.65:
                F_dz1 = 0
            else:
                if (period[ip] >= 0.65 and abs(dz1) <= (dict["f7"][ip]/dict["f6"][ip])):
                    F_dz1 = dict["f6"][ip] * dz1
                else:
                    F_dz1=dict["f7"][ip]
        else:
            F_dz1 = 0

        F_S = ln_Flin + ln_Fnlin + F_dz1
        ln_Y = F_E + F_P + F_S
        median = np.exp(ln_Y)

    else:
        ln_y = F_E + F_P
        median = np.exp(ln_y)
        
    # Aleatory - uncertainty function

    if M <= 4.5:
        tau = dict["tau1"][ip]
        phi_M = dict["phi1"][ip]
    elif (4.5 < M and M < 5.5):
        tau = dict["tau1"][ip] + (dict["tau2"][ip] - dict["tau1"][ip]) * (M - 4.5)
        phi_M = dict["phi1"][ip] + (dict["phi2"][ip] - dict["phi1"][ip]) * (M - 4.5)
    else:
        tau = dict["tau2"][ip]
        phi_M = dict["phi2"][ip]
        
    if Rjb <= dict["R1"][ip]:
        phi_MR = phi_M
    elif (dict["R1"][ip] < Rjb and Rjb <= dict["R2"][ip]):
        phi_MR = phi_M + dict["dphiR"][ip] * (np.log(Rjb/dict["R1"][ip]) / np.log(dict["R2"][ip]/dict["R1"][ip]))
    else:
        phi_MR = phi_M + dict["dphiR"][ip]
        
    if Vs30 >= v2:
        phi_MRV = phi_MR
    elif (v1 <= Vs30 and Vs30 <= v2):
        phi_MRV = phi_MR - dict["dphiV"][ip] * (np.log(v2/Vs30) / np.log(v2/v1))
    else:
        phi_MRV = phi_MR - dict["dphiV"][ip]

    sigma = np.sqrt(phi_MRV ** 2 + tau ** 2)

    return median, sigma


def gmpe_BSSA_2014(M, T, Rjb, Fault_Type, region, z1, Vs30):
    period = [-1, 0, 0.01, 0.02, 0.03, 0.05, 0.075, 0.1, 0.15, 0.2, 0.25, 0.3, 0.4, 0.5, 0.75, 1, 1.5, 2, 3, 4, 5, 7.5, 10]
    
    U = (Fault_Type == 0)
    SS = (Fault_Type == 1)
    NS = (Fault_Type == 2)
    RS = (Fault_Type == 3)
    
    if type(T) is not list:
        T = [T]    
    if (len(T) == 1 and T == 1000): # Compute median and sigma with pre-defined period
        median = np.zeros((1,len(period)-2))
        sigma = np.zeros((1,len(period)-2))
        period1 = period[2:]
        for ip in range(2, len(period)):
            median[ip-2],sigma[ip-2] = BSSA_2014_sub(M, ip, Rjb, U, SS, NS, RS, region, z1, Vs30)       
            
    else:                            # Compute median and sigma with user-defined period
        median = np.zeros((1, len(T)))
        sigma = np.zeros((1, len(T)))
        period1 = T
        
        for i in range(len(T)):
            Ti = T[i]
            if len(np.where(abs(np.array(period)-Ti) < 0.0001)[0]) == 0: # The user defined period requires interpolation
                T_low = max(np.array(period)[np.array(period) < Ti])
                T_high = min(np.array(period)[np.array(period) > Ti])
                ip_low  = period.index(T_low)
                ip_high = period.index(T_high)

                Sa_low, sigma_low = BSSA_2014_sub(M, ip_low, Rjb, U, SS, NS, RS, region, z1, Vs30)
                Sa_high, sigma_high = BSSA_2014_sub(M, ip_high, Rjb, U, SS, NS, RS, region, z1, Vs30)

                x = [np.log(T_low), np.log(T_high)]
                Y_sa = [np.log(Sa_low), np.log(Sa_high)]
                Y_sigma = [sigma_low, sigma_high]
                interpF1 = interp1d(x, Y_sa)
                median[i] = np.exp(interpF1(np.log(Ti)))
                interpF2 = interp1d(x, Y_sigma)
                sigma[i] = interpF2(np.log(Ti))
            else:
                ip_T = np.where(abs(np.array(period) - Ti) < 0.0001)[0][0]
                median[i], sigma[i] = BSSA_2014_sub(M, ip_T, Rjb, U, SS, NS, RS, region, z1, Vs30)

    return median[0][0], sigma[0][0], period1