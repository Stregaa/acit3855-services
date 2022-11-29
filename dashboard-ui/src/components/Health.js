import React, { useEffect, useState } from 'react'
import '../App.css';

export default function Health() {
    const [isLoaded, setIsLoaded] = useState(false);
    const [stats, setStats] = useState({});
    const [error, setError] = useState(null)

	const getStats = () => {
	
        fetch(`http://kafka.japaneast.cloudapp.azure.com:8120/health`)
            .then(res => res.json())
            .then((result)=>{
				console.log("Health Check")
                setStats(result);
                setIsLoaded(true);
            },(error) =>{
                setError(error)
                setIsLoaded(true);
            })
    }
    useEffect(() => {
		const interval = setInterval(() => getStats(), 2000); // Update every 2 seconds
		return() => clearInterval(interval);
    }, [getStats]);

    if (error){
        return (<div className={"error"}>Error found when fetching from API</div>)
    } else if (isLoaded === false){
        return(<div>Loading...</div>)
    } else if (isLoaded === true){
        return(
            <div>
                <h1>Health Check</h1>
                <table className={"StatsTable"}>
					<tbody>
						<tr>
							<th>Health Check</th>
						</tr>
						<tr>
							<td>Receiver: {stats['receiver']}</td>
							<td>Storage: {stats['storage']}</td>
						</tr>
						<tr>
							<td>Processing: {stats['processing']}</td>
						</tr>
						<tr>
							<td>Audit: {stats['audit']}</td>
						</tr>
					</tbody>
                </table>
                <h3>Last Updated: {stats['last_updated']}</h3>

            </div>
        )
    }
}
