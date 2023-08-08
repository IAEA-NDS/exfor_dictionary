####################################################################
#
# This file is part of exfor-parser.
# Copyright (C) 2022 International Atomic Energy Agency (IAEA)
#
# Disclaimer: The code is still under developments and not ready
#             to use. It has been made public to share the progress
#             among collaborators.
# Contact:    nds.contact-point@iaea.org
#
####################################################################

### Abbreviations in the EXFOR dictionary

reaction_abbr = {
    "abun.": "abundance",
    "abund.": "abundance",
    "abs.": "absolute",
    "ave.": "average",
    "avg.": "average",
    "aver.": "average",
    "ang.": "angle",
    "analyz.": "analyzing",
    "anal.": "analyzing",
    "beamcurr.": "beam current",
    "chrg.": "charge",
    "chan.": "channel",
    "ch.": "channel",
    "cs.": "cross section",
    #  "contr.": "what?",
    "comp.": "compound",
    "coef.": "Coefficient",
    "corr.": "correlated",
    "correl.": "correlated",
    "curr.": "current",
    "cum.": "cumulative",
    "Contrib.": "Contribution",
    "doub.": "double",
    "diff.": "differencial",
    "diff.cs": "differencial cross section",
    "distr.": "distribution",
    "dist.": "distribution",
    # "dir.": "Direct?",
    "dep.": "dependent",
    "del.": "delayed",  # e.g. in Dl/GRp,siG,n
    "electr.": "electrical",
    "elec.": "electric",
    "E.": "energy",
    "en.": "energy",
    "ene.": "energy",
    "energ.": "energy",
    "emiss.": "emission",
    "em.": "emission",
    "exc.": "excitation",
    "excl.": "excluding",
    "evap.": "evapolation",
    #  "f.": "fragment or factor or fission or for or final",  # use cases of factor:pAR,pOl/DA/DA/DE,,AnA, for: CHn,siG,
    # "f.thick": "For thick target?",
    "frag.": "fragment",
    "fr.": "fragment",
    "fragm.": "fragment",
    "fis.": "fission",
    "fiss.": "fission",
    "fn.": "function",
    "fct.": "function",  # in ttY
    "fct.": "factor",  # in general
    "form.": "formation",
    "gam.": "gamma",
    "grp.": "group",
    "gvn": "given",  # in Dl/GRp/pAR,nU
    "giv.": "given",
    "inc.": "incident",
    "incid.": "incident",
    "interm.": "intermediate",
    "isot.": "isotope",
    "ind.": "independent",
    "indep.": "independent",
    "independ.": "independent",
    "incl.": "including",
    "iso.": "isomeric",
    "isom.": "isomeric",
    "Isomer.": "Isomeric",
    "int.": "integrate",
    "integr.": "integrate",
    "interact.": "interaction",
    "kin.": "Kinetic",
    "leg.": "legendle",
    "longit.": "longitudinal",
    "longitud.": "longitudinal",
    "mom.": "momentumn",
    "maxw.": "maxwellian",
    "maxwell.": "maxwellian",
    "mult.": "multiplicity",
    "multipl.": "multiplicity",
    "nat.": "natural",
    "neut.": "neutron",
    "neutr.": "neutron",
    "ntr.": "neutron",
    "no.": "number",
    "nuc.": "nuclide",
    "nucl.": "nuclide",
    #  "oth.": "What?",  # other?
    #  "ot.": "What?",   # other than?
    "outg.": "outgoing",
    "param.": "parameter",
    "part.": "particle",
    "partl.": "particle",
    "proj.": "projectile",
    "prod.": "product",  # for FY and other
    "prod.": "production",  # for ttY
    "pr.": "primary",
    "prim.": "primary",
    "prob.": "probable",
    "par.": "partial",
    "ptl.": "partial",
    "Pol.": "Polarization",
    "polar.": "polarized",
    "phys.": "physical",
    "Pro.": "Production",
    "reac.": "reaction",
    "reson.": "resonance",
    "rel.": "relative",
    "red.": "reduced",
    "rot.": "rotation",
    "resid.": "residual",
    "saturat.": "saturated",
    "sect.": "section",
    "sec.": "section",  # hope it's not secondary
    "seq.": "sequence",
    "spec.": "specified",
    "specif.": "specified",
    "spect.": "spectrum",
    "sys.": "system",
    "targ.": "target",
    "Tar.": "Target",
    "tot.": "total",
    "ter.": "ternary",
    "tern.": "ternary",
    "ternar.": "ternary",
    "trans.": "transition",
    "Transv.": "Transversely",
    "temp": "temperature",
    "yld.": "yield",
    "Vect.": "vector",
    "w.r.t": "with respect to",
    "w.resp.to": "with respect to",
    "unc.": "uncertainty",
    "uncert.": "Uncertainty",
    "uncor.": "uncorrelated",
    "unspec.": "unspecified",
}


#### Abbreviations of units
head_unit_abbr = {
    "addit.": "additional",
    "c.m.": "Center of mass",
    "degradat.": "degradation",
    "en.": "energy",
    "equiv.": "equivalent",
    "lab.": "laboratory",
    "inc.": "incident",
    "incid.": "incident",
    "part.": "particle",
    "particl.": "particle",
    "proj.": "projectile",
    "sys.": "system",
}


#### Abbreviations of journal and report
journal_abbr = {
    "Astr.": "Astrophysics",
    "Acad.": "Academic",
    "Bull.": "Bulletin",
    "Conf.": "Conference",
    "Fac.": "Facility",
    "Fiz.": "Fizika",
    "int.": "international",
    "inst.": "institute",
    "Jour.": "Journal",
    "J.": "Journal",
    "nucl.": "nuclear",
    "math.": "mathmatics",
    "phys.": "physics",
    "proc.": "proceedings",
    "suppl.": "supplemental",
    "sect.": "section",
    "sci.": "science",
    "symp.": "symmposium",
    "Univ.": "University",
}


institute_abbr = {
    # "Adm.": "what?",
    "Acad.": "Academy",
    "Accel.": "Accelerator",
    "Centr.": "Center",
    "Develop.": "Development",
    "Dept.": "Department",
    "Div.": "Division",
    "Elect.": "Electoric",
    "En.": "Energy",
    "Fac.": "Facility",
    "Facil.": "Facility",
    "Facult.": "Faculty",
    "Int.": "International",
    "Internat.": "International",
    "inst.": "Institute",
    "Inst.": "Institute",
    "instit.": "Instituto",  # in 3BZl
    "Info.": "Information",
    "Lab.": "Laboratory",
    "lab.": "laboratory",
    "math.": "mathmatics",
    "mathem.": "mathmatics",
    "Nat.": "National",
    "Nucl.": "Nuclear",
    "Nuc.": "Nuclear",
    "Occupat.": "Occupational",
    "math.": "mathmatics",
    "phys.": "physics",
    "Phys.": "Physics",
    "res.": "research",
    "Res.": "Research",
    "sect.": "section",
    "sci.": "science",
    "techn.": "technology",
    "Univ.": "University",
}


def convert_abbreviations(abb_dict, desc):
    for abb, corr in abb_dict.items():
        desc = desc.replace(abb, corr + " ")
    return desc.replace(
        "  ", " "
    )  # or desc.title().replace("  ", " ") or desc.capitalize().replace("  ", " ")


if __name__ == "__main__":
    desc = "abun. of frag."
    convert_abbreviations(reaction_abbr, desc)
