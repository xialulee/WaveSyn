function pid = matlabPID()
import System.Diagnostics.*
process = System.Diagnostics.Process.GetCurrentProcess();
pid = process.Id;
end