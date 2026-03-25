# Calculate WQI based on Perduce University WQI formula
# Default values for BOD and conductivity are based on typical values for freshwater lakes
def calculate_wqi(temp, tss, do, bod=2, cond=160):
    # 1. Temperature Index (ITEMP)
    if temp <= 20:
        i_temp = 1.0
    else:
        i_temp = max(0, 1.0 - 0.1 * (temp - 20))
        
    # 2. Biological Oxygen Demand Index (IBOD)
    if bod >= 12:
        i_bod = 0
    else:
        i_bod = max(0, 30 * (1 - bod / 12))
        
    # 3. Total Suspended Solids Index (ITSS)
    if tss >= 250:
        i_tss = 0
    else:
        i_tss = max(0, 25 * (1 - tss / 250))
        
    # 4. Dissolved Oxygen Index (IDO)
    if do >= 10:
        i_do = 25
    elif do <= 0:
        i_do = 0
    else:
        i_do = 2.5 * do
        
    # 5. Conductivity Index (ICOND)
    if cond <= 200:
        i_cond = 20
    elif cond >= 4000:
        i_cond = 0
    else:
        i_cond = 20 * (1 - (cond - 200) / (4000 - 200))
        
    # Master Calculation
    wqi = i_temp * (i_bod + i_tss + i_do + i_cond)
    
    # Quality Categorization
    if wqi >= 95:
        rating = "Excellent"
    elif wqi >= 75:
        rating = "Good"
    elif wqi >= 50:
        rating = "Fair"
    else:
        rating = "Poor"
        
    return {
        "WQI": round(wqi, 2),
        "Rating": rating
    }