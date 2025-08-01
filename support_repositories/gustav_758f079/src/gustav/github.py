import pandas as pd

from gustav import inout


def gender_guesser():
    """
    Information of gender frequencies from
    https://github.com/lead-ratings/gender-guesser
    
    Documentation and license from source data:
    
    # DO NOT CHANGE:   FILE-FORMAT DEFINITION-DATE = 2008-11-16                           $
    #                                                                                     $
    # nam_dict.txt                                                                        $
    # ------------                                                                        $
    #                                                                                     $
    # List of first names and gender.                                                     $
    #                                                                                     $
    # Copyright (c):                                                                      $
    # 2007-2008:  Jörg MICHAEL, Adalbert-Stifter-Str. 11,                                 $
    #             30655 Hannover, Germany                                                 $
    #                                                                                     $
    # SCCS: @(#) nam_dict.txt  1.2  2008-11-30                                            $
    #                                                                                     $
    # This file is subject to the GNU Free Documentation License.                         $
    # Permission is granted to copy, distribute and/or modify                             $
    # this document under the terms of the GNU Free Documentation                         $
    # License, Version 1.2 or any later version published by the                          $
    # Free Software Foundation; with no Invariant Sections,                               $
    # no Front-Cover Texts, and no Back-Cover Texts.                                      $
    #                                                                                     $
    # This file is distributed in the hope that it will be useful,                        $
    # but WITHOUT ANY WARRANTY; without even the implied warranty                         $
    # of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.                             $
    #                                                                                     $
    # A copy of the license can be found in the file GNU_DOC.TXT.                         $
    # You should have received a copy of the GNU Free Documentation                       $
    # License along with this file;                                                       $
    # if not, write to the  Free Software Foundation, Inc.,                               $
    # 675 Mass Ave, Cambridge, MA 02139, USA.                                             $
    #                                                                                     $
    # There is one important restriction:                                                 $
    # If you modify this file in any way (e.g. add some data),                            $
    # you must also release the changes under the terms of the                            $
    # GNU Free Documentation License.                                                     $
    #                                                                                     $
    # That means you have to give out your changes, and a very good                       $
    # way to do so is mailing them to the address given below.                            $
    # I think this is the best way to promote further development                         $
    # and use of this file.                                                               $
    #                                                                                     $
    # If you have any remarks, feel free to e-mail to:                                    $
    #     ct@ct.heise.de                                                                  $
    #                                                                                     $
    # The author's email address is:                                                      $
    #    astro.joerg@googlemail.com                                                       $
    #                                                                                     $
    #                                                                                     $
    ##################################################################################    $
    ###  char set  ###################################################################    $
    ##################################################################################    $
    #                                                                                     $
    # char set = utf-8                                                                    $
    #                                                                                     $
    # A plus char ('+') "inside" a name symbolizes a '-', ' ' or an empty string          $
    # (this option applies to Arabic, Chinese and Korean names only).                     $
    # Thus, "Jun+Wei" represents the names "Jun-Wei", "Jun Wei" and "Junwei".             $
    #                                                                                     $
    #                                                                                     $
    ##################################################################################    $
    ###  syntax of name list  ########################################################    $
    ##################################################################################    $
    #                                                                                     $
    # # = comment                                                                         $
    #                                                                                     $
    #                                                                                     $
    # Syntax for "normal" name list (do not change):                                      $
    #                                                                                     $
    #    M  <male first name>                                                             $
    #    1M <male name, if first part of name;                                            $
    #            else: mostly male name>                                                  $
    #    ?M <mostly male name (= unisex name, which is mostly male)>                      $
    #                                                                                     $
    #    F  <female first name>                                                           $
    #    1F <female name, if first part of name;                                          $
    #            else: mostly female name>                                                $
    #    ?F <mostly female name (= unisex name, which is mostly female)>                  $
    #                                                                                     $
    #    ?  <unisex name (= can be male or female)>                                       $
    #                                                                                     $
    #                                                                                     $
    # Syntax for "equivalent" names (do not change):                                      $
    #                                                                                     $
    #    =  <short_name> <long_name>                                                      $
    #                                                                                     $
    #                                                                                     $   
    """

    data_version = inout.get_data_version('gender_guesser')

    p = inout.get_input_path(
        'github/gender_guesser/{}/gender_frequencies.parquet'.format(
            data_version)
    )
    df = pd.read_parquet(p)
    return df


def maggiecrow_deprior():
    """
    DE Prior, a measure differential expressability by 
    Crow et al. 2019 https://www.pnas.org/content/116/13/6491.short
    """

    data_version = inout.get_data_version('deprior')

    p = inout.get_input_path(
        'github/maggiecrow/deprior/{}/de_prior.parquet'.format(
            data_version)
    )
    df = pd.read_parquet(p)
    return df
