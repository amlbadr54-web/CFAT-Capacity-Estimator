"""CFAT capacity estimator: Python standard library only."""
import json, math, pathlib, tkinter as tk
from tkinter import ttk, messagebox, filedialog
ROOT=pathlib.Path(__file__).resolve().parent
MODEL=json.loads((ROOT/'model.json').read_text())
def predict(v):
    if any(not math.isfinite(x) for x in v.values()): raise ValueError('All inputs must be finite numbers.')
    if any(v[k]<=0 for k in ['D','t','L','fc','sigma02']) or v['e']<0: raise ValueError('Dimensions and strengths must be positive; eccentricity must be zero or positive.')
    if v['D']<=2*v['t']: raise ValueError('Outer diameter must exceed twice the wall thickness (D > 2t).')
    D,t=v['D'],v['t'];aa=math.pi*(D*D-(D-2*t)**2)/4;ac=math.pi*(D-2*t)**2/4
    x=[math.log(aa),math.log(ac),math.log(v['L']/D),math.log1p(v['e']/D),math.log(v['sigma02']),math.log(v['fc'])]
    warnings=[]
    for k,(lo,hi) in MODEL['ranges'].items():
        if not lo<=v[k]<=hi: warnings.append(f'{k} outside experimental range ({lo:g}–{hi:g}).')
    for k,val in [('L/D',v['L']/D),('e/D',v['e']/D)]:
        lo,hi=MODEL['derived_ranges'][k]
        if not lo<=val<=hi: warnings.append(f'{k} outside experimental range ({lo:.3g}–{hi:.3g}).')
    if warnings:return None,aa,ac,warnings
    capacity=math.exp(MODEL['intercept']+sum(b*z for b,z in zip(MODEL['coefficients'],x)))
    return capacity,aa,ac,[]
class App:
    def __init__(self,root):
        self.root=root;self.result=None;root.title('CFAT | Capacity Estimator');root.geometry('1040x720');root.minsize(950,690);root.configure(bg='#f2f5f8')
        st=ttk.Style();st.theme_use('clam');st.configure('TLabel',font=('Segoe UI',11),background='#ffffff',foreground='#24384a');st.configure('TEntry',padding=7,font=('Segoe UI',12));st.configure('TButton',font=('Segoe UI',11),padding=10);st.configure('Primary.TButton',background='#176c88',foreground='white');st.configure('TFrame',background='white')
        header=tk.Frame(root,bg='#163249',padx=28,pady=20);header.pack(fill='x');tk.Label(header,text='CFAT  |  Capacity Estimator',font=('Segoe UI',23,'bold'),bg='#163249',fg='white').pack(anchor='w');tk.Label(header,text='Circular concrete-filled aluminum tubular columns',font=('Segoe UI',12),bg='#163249',fg='#c6dbe6').pack(anchor='w',pady=(5,0))
        body=tk.Frame(root,bg='#f2f5f8');body.pack(fill='both',expand=True,padx=24,pady=20);body.columnconfigure(0,weight=3);body.columnconfigure(1,weight=2);body.rowconfigure(0,weight=1)
        left=ttk.Frame(body,padding=20);left.grid(row=0,column=0,sticky='nsew',padx=(0,18));left.columnconfigure(1,weight=1)
        ttk.Label(left,text='Column geometry and materials',font=('Segoe UI',15,'bold')).grid(row=0,column=0,columnspan=3,sticky='w',pady=(0,18))
        self.vars={};fields=[('D','Outer diameter, D','mm'),('t','Wall thickness, t','mm'),('L','Column length, L','mm'),('e','Load eccentricity, e','mm'),('fc','Reported concrete strength, fc','MPa'),('sigma02','Aluminum proof stress, σ0.2','MPa')]
        for i,(key,label,unit) in enumerate(fields,1):
            ttk.Label(left,text=label).grid(row=2*i-1,column=0,sticky='w',padx=(0,12));v=tk.StringVar();self.vars[key]=v;ttk.Entry(left,textvariable=v,width=13).grid(row=2*i-1,column=1,sticky='ew');ttk.Label(left,text=unit).grid(row=2*i-1,column=2,padx=8)
            lo,hi=MODEL['ranges'][key];ttk.Label(left,text=f'Experimental range: {lo:g}–{hi:g} {unit}',font=('Segoe UI',9),foreground='#647685').grid(row=2*i,column=0,columnspan=3,sticky='w',pady=(2,10));v.trace_add('write',self.invalidate)
        buttons=ttk.Frame(left);buttons.grid(row=13,column=0,columnspan=3,sticky='ew',pady=(10,0));ttk.Button(buttons,text='Estimate capacity',style='Primary.TButton',command=self.calculate).pack(side='left');ttk.Button(buttons,text='Load example',command=self.example).pack(side='left',padx=8)
        right=ttk.Frame(body,padding=22);right.grid(row=0,column=1,sticky='nsew');ttk.Label(right,text='Estimated ultimate capacity',font=('Segoe UI',13,'bold')).pack(anchor='w');self.number=tk.StringVar(value='—');ttk.Label(right,textvariable=self.number,font=('Segoe UI',32,'bold'),foreground='#176c88').pack(anchor='w',pady=(22,3));ttk.Label(right,text='kN',font=('Segoe UI',15)).pack(anchor='w');self.details=tk.StringVar(value='Enter six inputs to calculate.');ttk.Label(right,textvariable=self.details,wraplength=330,justify='left').pack(anchor='w',pady=22)
        self.export=ttk.Button(right,text='Export calculation report',command=self.save,state='disabled');self.export.pack(anchor='w');ttk.Separator(right).pack(fill='x',pady=23)
        ttk.Label(right,text='Model information',font=('Segoe UI',12,'bold')).pack(anchor='w');ttk.Label(right,text='Geometry-based ridge · Version 1.0\n98 experimental training records\nPositive capacity formulation',wraplength=330,justify='left').pack(anchor='w',pady=8)
        ttk.Label(right,text='Research estimate, not a design resistance. Range checks do not establish coverage of every input combination. Concrete strength retains the source-reported test basis.',wraplength=330,justify='left',font=('Segoe UI',10),foreground='#647685').pack(anchor='w',pady=12)
        root.bind('<Return>',lambda e:self.calculate())
    def invalidate(self,*args):
        self.result=None
        if hasattr(self,'number'):self.number.set('—');self.details.set('Inputs changed. Recalculate to update the result.');self.export.configure(state='disabled')
    def example(self):
        for k,v in json.loads((ROOT/'reference_cases.json').read_text())[0]['inputs'].items():self.vars[k].set(f'{v:g}')
        self.calculate()
    def calculate(self):
        self.invalidate()
        try:
            v={k:float(x.get()) for k,x in self.vars.items()};n,aa,ac,w=predict(v)
            if w:self.details.set('Outside model range. Prediction withheld.\n\n'+'\n'.join(w));return
            self.result={'inputs':v,'estimated_capacity_kN':n,'aluminum_area_mm2':aa,'concrete_area_mm2':ac,'model_version':MODEL['version'],'status':'Exploratory estimate; not design resistance'};self.number.set(f'{n:,.2f}');self.details.set(f'Aluminum area: {aa:,.1f} mm²\nConcrete area: {ac:,.1f} mm²\nL/D: {v["L"]/v["D"]:.3f}\ne/D: {v["e"]/v["D"]:.3f}\n\nInputs pass range checks.');self.export.configure(state='normal')
        except (ValueError,OverflowError) as ex:messagebox.showerror('Check inputs',str(ex))
    def save(self):
        if self.result is None:return
        f=filedialog.asksaveasfilename(defaultextension='.json',filetypes=[('Calculation report','*.json')])
        if f:pathlib.Path(f).write_text(json.dumps(self.result,indent=2))
if __name__=='__main__':App(tk.Tk());tk.mainloop()
